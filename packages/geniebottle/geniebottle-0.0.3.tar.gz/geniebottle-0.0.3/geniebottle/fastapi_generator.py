"""
FastAPI server generator for Magic spells.

This module automatically generates FastAPI endpoints from Magic spells,
with type validation, proper error handling, and OpenAPI documentation.
"""

import inspect
import base64
import json
from io import BytesIO
from typing import Any, Dict, get_type_hints, get_origin, get_args, Union
from PIL import Image

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from geniebottle.utils import extract_docstring_description
from geniebottle.model_utils import create_request_model_from_spell


def serialize_output(output: Any) -> Any:
    """
    Serialize spell output for JSON response.

    Handles special types like PIL Images, BytesIO, etc.

    Args:
        output: The spell output to serialize

    Returns:
        JSON-serializable output
    """
    if isinstance(output, Image.Image):
        # Convert PIL Image to base64
        buffered = BytesIO()
        output.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return {
            "type": "image",
            "format": "png",
            "data": img_str
        }

    elif isinstance(output, BytesIO):
        # Convert BytesIO to base64
        data_str = base64.b64encode(output.getvalue()).decode()
        return {
            "type": "binary",
            "data": data_str
        }

    elif isinstance(output, (list, tuple)):
        # Recursively serialize lists/tuples
        return [serialize_output(item) for item in output]

    elif isinstance(output, dict):
        # Recursively serialize dicts
        return {key: serialize_output(value) for key, value in output.items()}

    else:
        # Return as-is for JSON-serializable types
        return output


def normalize_event(output: Any) -> Dict[str, Any]:
    """
    Normalize any spell output to {type, payload} format for consistent SSE streaming.

    This creates a uniform event structure regardless of the spell's output type:
    - Agent spell dicts like {"spell_name": "text_response"} → {"type": "spell_name", "payload": "text_response"}
    - ChatGPT strings like "Hello" → {"type": "output", "payload": "Hello"}
    - Done booleans → {"type": "done", "payload": true}
    - Other types → {"type": "data", "payload": ...}

    Args:
        output: The raw output from a spell

    Returns:
        Dict with "type" and "payload" keys
    """
    if isinstance(output, dict):
        # Agent-style structured events: extract the key as the type
        if len(output) == 1:
            event_type = list(output.keys())[0]
            return {"type": event_type, "payload": output[event_type]}
        else:
            # Multi-key dict, treat as data
            return {"type": "data", "payload": output}
    elif isinstance(output, str):
        # Simple text streaming (chatgpt, text_response, etc.)
        return {"type": "output", "payload": output}
    elif isinstance(output, bool):
        # Done signals
        return {"type": "done", "payload": output}
    elif isinstance(output, (Image.Image, BytesIO)):
        # Images and files - serialize and send as output (JSON string)
        serialized = serialize_output(output)
        return {"type": "output", "payload": json.dumps(serialized)}
    elif isinstance(output, list):
        # Arrays - treat as result
        return {"type": "result", "payload": serialize_output(output)}
    else:
        # Fallback for any other type
        return {"type": "data", "payload": output}


def is_generator_function(func):
    """Check if a function is a generator function."""
    return inspect.isgeneratorfunction(func) or inspect.isasyncgenfunction(func)


def is_generator(obj):
    """Check if an object is a generator."""
    return inspect.isgenerator(obj) or inspect.isasyncgen(obj)


def create_fastapi_app_from_magic(magic) -> FastAPI:
    """
    Create a FastAPI application from a Magic instance.

    This automatically generates REST API endpoints for all spells in the Magic instance,
    with proper type validation, error handling, and OpenAPI documentation.

    Args:
        magic: The Magic instance containing spells to serve

    Returns:
        FastAPI: A configured FastAPI application

    Example:
        >>> from geniebottle import Magic
        >>> from geniebottle.spellbooks import OpenAI
        >>> magic = Magic()
        >>> magic.add(OpenAI().get('chatgpt'))
        >>> app = create_fastapi_app_from_magic(magic)
    """
    # Create FastAPI app with metadata
    app = FastAPI(
        title="Magic Spells API",
        description="Auto-generated REST API for Magic spells",
        version="1.0.0",
    )

    # Add CORS middleware for web clients
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure this based on your security needs
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create endpoints for each spell
    for spell in magic.spells:
        spell_name = spell.__name__

        # Get spell description from docstring
        spell_doc = inspect.getdoc(spell) or f"Cast the {spell_name} spell"
        spell_description = extract_docstring_description(spell_doc) or spell_doc

        # Create Pydantic model for request validation
        request_model = create_request_model_from_spell(spell)

        # Check if spell is a generator (streaming)
        is_streaming = is_generator_function(spell)

        if is_streaming:
            # Create streaming endpoint using Server-Sent Events
            async def create_streaming_endpoint(spell_func):
                async def endpoint(request: request_model):
                    try:
                        # Call spell with request parameters
                        params = request.dict(exclude_unset=True)

                        async def generate():
                            try:
                                for chunk in spell_func(**params):
                                    # Extract output from tuple if present (drop context)
                                    if isinstance(chunk, tuple) and len(chunk) >= 1:
                                        output = chunk[0]
                                    else:
                                        output = chunk

                                    # Normalize to {type, payload} format
                                    event = normalize_event(output)

                                    # Send as Server-Sent Event with proper JSON
                                    yield f"data: {json.dumps(event)}\n\n"
                            except Exception as e:
                                yield f"data: {json.dumps({'type': 'error', 'payload': str(e)})}\n\n"

                        return StreamingResponse(
                            generate(),
                            media_type="text/event-stream"
                        )

                    except Exception as e:
                        raise HTTPException(status_code=500, detail=str(e))

                return endpoint

            endpoint_func = create_streaming_endpoint(spell)

        else:
            # Create regular endpoint (but handle runtime generators)
            def create_endpoint(spell_func):
                async def endpoint(request: request_model):
                    try:
                        # Call spell with request parameters
                        params = request.dict(exclude_unset=True)
                        result = spell_func(**params)

                        # Check if result is a generator at runtime
                        if is_generator(result):
                            # Handle as streaming response
                            def generate():
                                try:
                                    for chunk in result:
                                        # Extract output from tuple if present (drop context)
                                        if isinstance(chunk, tuple) and len(chunk) >= 1:
                                            output = chunk[0]
                                        else:
                                            output = chunk

                                        # Normalize to {type, payload} format
                                        event = normalize_event(output)

                                        # Send as Server-Sent Event with proper JSON
                                        yield f"data: {json.dumps(event)}\n\n"
                                except Exception as e:
                                    yield f"data: {json.dumps({'type': 'error', 'payload': str(e)})}\n\n"

                            return StreamingResponse(
                                generate(),
                                media_type="text/event-stream"
                            )
                        else:
                            # Serialize the result as regular JSON
                            serialized = serialize_output(result)
                            return JSONResponse(content={"result": serialized})

                    except Exception as e:
                        raise HTTPException(status_code=500, detail=str(e))

                return endpoint

            endpoint_func = create_endpoint(spell)

        # Set the function name and docstring for OpenAPI
        endpoint_func.__name__ = f"cast_{spell_name}"
        endpoint_func.__doc__ = spell_description

        # Register the endpoint
        app.post(
            f"/cast/{spell_name}",
            summary=f"Cast {spell_name} spell",
            description=spell_description,
            response_description="Spell casting result",
        )(endpoint_func)

    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "spells": len(magic.spells)}

    # Add info endpoint
    @app.get("/")
    async def info():
        spell_info = []
        for spell in magic.spells:
            spell_info.append({
                "name": spell.__name__,
                "description": extract_docstring_description(inspect.getdoc(spell) or ""),
                "endpoint": f"/cast/{spell.__name__}",
            })

        return {
            "message": "Magic Spells API",
            "spells": spell_info,
            "docs": "/docs",
        }

    return app
