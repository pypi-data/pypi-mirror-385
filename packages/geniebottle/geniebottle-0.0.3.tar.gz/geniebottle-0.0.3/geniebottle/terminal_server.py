"""
Web terminal server for interactive Magic agent access.

This module provides a web-based terminal interface using xterm.js
for interactive access to Magic agent scripts over WebSocket.
"""

import json
import asyncio
import sys
import io
import warnings
from pathlib import Path
from typing import Dict, Optional
from contextlib import redirect_stdout, redirect_stderr

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


class TerminalSession:
    """
    Manages a terminal session for a connected user.

    Each session maintains its own context, available_results, and system prompt.
    """

    def __init__(self, websocket: WebSocket, magic):
        self.websocket = websocket
        self.magic = magic
        self.context = []
        self.available_results = []
        self.system = "You are a helpful AI assistant."
        self.hide_warnings = False

    async def send_message(self, message: Dict):
        """Send a JSON message to the client."""
        await self.websocket.send_json(message)

    async def send_output(self, output: str):
        """Send output text to the terminal."""
        await self.send_message({"type": "output", "data": output})

    async def send_error(self, error: str):
        """Send error message to the terminal."""
        await self.send_message({"type": "error", "data": error})

    async def send_output_item(self, item):
        """
        Send an output item to the terminal.
        Handles any type: strings, images, audio, lists, dicts, etc.
        """
        import base64
        from io import BytesIO

        try:
            # Try to import PIL for image handling
            from PIL import Image
            has_pil = True
        except ImportError:
            has_pil = False

        # Handle different output types generically
        if isinstance(item, str):
            # Text output
            await self.send_output(f"\n{item}\n\n")

        elif isinstance(item, dict):
            # Dictionary output (might be structured data)
            await self.send_output(f"\n{json.dumps(item, indent=2)}\n\n")

        elif isinstance(item, list):
            # List output - could be images, strings, or other data
            if not item:
                await self.send_output("\n(empty list)\n\n")
                return

            # Check if list contains images
            if has_pil and isinstance(item[0], Image.Image):
                # Send images
                for i, img in enumerate(item):
                    await self.send_image(img, f"output_{i}")
            else:
                # Send as text list
                result_text = "\n"
                for list_item in item[:10]:
                    result_text += f"• {str(list_item)}\n"
                if len(item) > 10:
                    result_text += f"... and {len(item) - 10} more\n"
                await self.send_output(result_text + "\n")

        elif has_pil and isinstance(item, Image.Image):
            # Single image output
            await self.send_image(item, "output")

        elif isinstance(item, bytes):
            # Binary data (could be audio, etc.)
            await self.send_message({
                "type": "binary",
                "data": base64.b64encode(item).decode('utf-8'),
                "size": len(item)
            })

        elif isinstance(item, bool):
            # Boolean result
            if item:
                await self.send_output("\n✓ Success\n\n")
            else:
                await self.send_error("\n✗ Failed\n\n")

        else:
            # Unknown type - convert to string
            await self.send_output(f"\n{str(item)}\n\n")

    async def send_image(self, image, name="image"):
        """Send an image to the terminal (as base64 data URL for display)."""
        from io import BytesIO
        import base64

        # Convert PIL Image to base64 data URL
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        img_data = buffer.getvalue()
        img_base64 = base64.b64encode(img_data).decode('utf-8')

        await self.send_message({
            "type": "image",
            "data": img_base64,
            "name": name,
            "width": image.size[0],
            "height": image.size[1]
        })

    async def handle_command(self, command: str):
        """Handle special commands like /help, /system, etc."""
        command = command.strip()

        if command == "/help":
            help_text = (
                "\n📖 Available Commands:\n\n"
                "/help - Show this help message\n"
                "/system - Change the system prompt\n"
                "/hide-warnings - Toggle warning display on/off\n"
                "/clear - Clear context and results\n\n"
            )
            await self.send_output(help_text)
            return True

        elif command == "/system":
            await self.send_output("\nEnter new system prompt (or press enter to keep current):\n> ")
            await self.send_message({"type": "prompt_system"})
            return True

        elif command.startswith("/system "):
            new_system = command[8:].strip()
            if new_system:
                self.system = new_system
                await self.send_output("✓ System prompt updated\n")
            return True

        elif command == "/hide-warnings":
            self.hide_warnings = not self.hide_warnings
            status = "hidden" if self.hide_warnings else "shown"
            await self.send_output(f"✓ Warnings will now be {status}\n")
            return True

        elif command == "/clear":
            self.context = []
            self.available_results = []
            await self.send_output("✓ Context and results cleared\n")
            return True

        return False

    async def process_input(self, user_input: str):
        """Process user input and cast magic spells."""
        # Handle commands
        if user_input.startswith("/"):
            is_command = await self.handle_command(user_input)
            if is_command:
                return

        try:
            # Dynamically detect the correct parameter name for the spell
            # Try common parameter names: 'input', 'user_input', 'prompt', 'text'
            import inspect

            param_name = 'input'  # default fallback
            if self.magic.spells:
                sig = inspect.signature(self.magic.spells[0])
                params = list(sig.parameters.keys())

                # Check for common input parameter names in priority order
                for candidate in ['user_input', 'input', 'prompt', 'text', 'query']:
                    if candidate in params:
                        param_name = candidate
                        break

            # Call magic.cast() with the dynamically determined parameter name
            outputs = self.magic.cast(**{param_name: user_input})

            # Iterate over whatever the generator yields
            for item in outputs:
                # Send the output to the terminal
                await self.send_output_item(item)

        except Exception as e:
            import traceback
            await self.send_error(f"\nAn error occurred: {e}\n\n{traceback.format_exc()}\n")


async def handle_websocket(websocket: WebSocket, magic, welcome_message=None):
    """
    Handle WebSocket connection for a terminal session.

    Args:
        websocket: The WebSocket connection
        magic: The Magic instance
        welcome_message: Optional custom welcome message. If None, generates one based on available spells.
    """
    await websocket.accept()

    # Create session
    session = TerminalSession(websocket, magic)

    # Generate welcome message if not provided
    if welcome_message is None:
        # Generate list of available spells
        spell_list = []
        for spell in magic.spells:
            spell_name = spell.__name__ if hasattr(spell, '__name__') else str(spell)
            spell_list.append(f"  • {spell_name}")

        spell_info = "\r\n".join(spell_list) if spell_list else "  • No spells available"

        welcome_message = (
            "\r\n✨ Magic Terminal\r\n\r\n"
            "Available spells:\r\n"
            f"{spell_info}\r\n\r\n"
            "Type your request to cast spells.\r\n"
            "/help for commands\r\n\r\n"
            "> "
        )
    else:
        # Ensure custom message ends with prompt
        if not welcome_message.endswith("> "):
            welcome_message += "\r\n> "

    await session.send_output(welcome_message)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            if data.get("type") == "input":
                user_input = data.get("data", "").strip()
                if user_input:
                    await session.process_input(user_input)
                    # Send prompt after processing input
                    await session.send_output("> ")

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")


def create_terminal_app(magic, welcome_message=None, no_confirm=False) -> FastAPI:
    """
    Create a FastAPI application for web terminal access.

    Args:
        magic: The Magic instance
        welcome_message: Optional custom welcome message. If None, generates one based on available spells.
        no_confirm: If True, auto-confirm all confirmation prompts (default: False)

    Returns:
        FastAPI: The configured FastAPI application
    """
    app = FastAPI(title="Magic Terminal")

    # Store no_confirm setting for access in WebSocket handler
    app.state.no_confirm = no_confirm

    # Get the path to static files
    static_dir = Path(__file__).parent / "static"

    # WebSocket endpoint
    @app.websocket("/terminal")
    async def websocket_endpoint(websocket: WebSocket):
        await handle_websocket(websocket, magic, welcome_message)

    # Serve the terminal HTML page
    @app.get("/")
    async def get_terminal():
        # Read the HTML template
        html_path = static_dir / "terminal.html"
        if html_path.exists():
            with open(html_path, 'r') as f:
                return HTMLResponse(content=f.read())
        else:
            # Return a basic HTML page if static files don't exist
            return HTMLResponse(content=get_basic_terminal_html())

    # Health check
    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


def get_basic_terminal_html() -> str:
    """
    Return a basic HTML page with xterm.js for the terminal.

    This is used as a fallback if static files are not available.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Magic Terminal</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.css" />
        <style>
            body {
                margin: 0;
                padding: 0;
                background: #000;
                font-family: monospace;
            }
            #terminal {
                width: 100vw;
                height: 100vh;
            }
        </style>
    </head>
    <body>
        <div id="terminal"></div>
        <script src="https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.js"></script>
        <script>
            const term = new Terminal({
                cursorBlink: true,
                fontSize: 14,
                theme: {
                    background: '#1e1e1e',
                    foreground: '#d4d4d4'
                }
            });
            term.open(document.getElementById('terminal'));

            const ws = new WebSocket(`ws://${window.location.host}/terminal`);

            let currentLine = '';

            ws.onopen = () => {
                term.write('\r\nConnected to Magic Agent\r\n\r\n');
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);

                if (data.type === 'output') {
                    term.write(data.data.replace(/\n/g, '\r\n'));
                } else if (data.type === 'error') {
                    term.write('\x1b[31m' + data.data.replace(/\n/g, '\r\n') + '\x1b[0m');
                } else if (data.type === 'spell_cast') {
                    term.write('\r\n\x1b[36m🪄 Casting ' + data.spell_name + '\x1b[0m\r\n\r\n');
                } else if (data.type === 'spell_args') {
                    term.write('\x1b[2m' + data.data + '\x1b[0m');
                } else if (data.type === 'warning') {
                    term.write('\r\n\x1b[33m⚠️  Warning: ' + data.data + '\x1b[0m\r\n');
                }

                term.write('💬 ');
            };

            ws.onclose = () => {
                term.write('\r\n\x1b[31mConnection closed\x1b[0m\r\n');
            };

            term.onData((data) => {
                const code = data.charCodeAt(0);

                // Handle Enter key
                if (code === 13) {
                    term.write('\r\n');
                    if (currentLine.trim()) {
                        ws.send(JSON.stringify({
                            type: 'input',
                            data: currentLine
                        }));
                    }
                    currentLine = '';
                }
                // Handle Backspace
                else if (code === 127) {
                    if (currentLine.length > 0) {
                        currentLine = currentLine.slice(0, -1);
                        term.write('\b \b');
                    }
                }
                // Handle Ctrl+C
                else if (code === 3) {
                    currentLine = '';
                    term.write('^C\r\n💬 ');
                }
                // Regular character
                else if (code >= 32 && code < 127) {
                    currentLine += data;
                    term.write(data);
                }
            });
        </script>
    </body>
    </html>
    """
