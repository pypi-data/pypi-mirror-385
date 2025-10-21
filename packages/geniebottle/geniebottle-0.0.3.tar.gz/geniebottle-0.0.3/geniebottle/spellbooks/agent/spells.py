from geniebottle import Magic
from geniebottle.decorators import limit_cost, agent_hint
from typing import Callable, Union
from pydantic import BaseModel, create_model, ValidationError
from typing import Iterator, Any
import inspect


@limit_cost(max_cost=0)
def done(done: bool):
    """Return a boolean value to indicate if the agent has completed the task and is done.
    Cast this spell when you are done with the task and need user input. This can only be casted as a spell and you cannot use
    `done=True` as an argument to any other spell.

    Args:
        done (bool): A boolean value to indicate if the agent has completed the task (true) or needs user input (false)
    """
    return done


@agent_hint(
    """Get the full content of a previous result by its index. Use this when a result is truncated and you need to see the complete content.

    Args:
        result_index (int): The index of the result to retrieve (e.g., 0 for results[0]).
    """
)
@limit_cost(max_cost=0)
def get_full_result(result_index: int, available_results: list[Any], **kwargs):
    """Get the full content of a previous result by its index.

    Args:
        result_index (int): The index of the result to retrieve.
        available_results (list): The list of available results.
    """
    if 0 <= result_index < len(available_results):
        return available_results[result_index]
    else:
        return f"Error: result_index {result_index} is out of range. Available indices: 0-{len(available_results)-1}"


def create_pydantic_model_from_function(func) -> BaseModel:
    """
    Create a Pydantic model based on the argument names and types of a function,
    making parameters required only if they don't have default values.

    Args:
        func (Callable): The function for which to create the Pydantic model.

    Returns:
        BaseModel: A Pydantic model with fields matching the function arguments.
    """
    # Get the function's signature
    sig = inspect.signature(func)
    fields = {}

    for name, param in sig.parameters.items():
        if param.annotation is param.empty:  # Skip if no type annotation is provided
            continue

        if param.default is param.empty:  # No default, make it required
            fields[name] = (param.annotation, ...)
        else:  # Has a default, make it optional
            fields[name] = (param.annotation, param.default)

    return create_model('DynamicModel', **fields)


class Agent:
    def __init__(
        self,
        brain_spell: Callable,
        spells_at_disposal: list[Callable],
        system_message: str,
        context: list[dict] = [],
        available_results: list[Any] = [],
        max_context_window_size: int = 100,
        max_cost_per_brain_cast: float = 1.5,
        max_cost_per_spell_cast: float = 1.5,
    ) -> None:
        self.brain = Magic(max_cost_per_cast=max_cost_per_brain_cast)
        self.brain.add(brain_spell)

        self.magic = Magic(max_cost_per_cast=max_cost_per_spell_cast)
        self.magic.add(spells_at_disposal)

        # Create wrapper for get_full_result that has access to available_results
        @agent_hint(
            """Get the full content of a previous result by its index. Use this when a result is truncated and you need to see the complete content.

            Args:
                result_index (int): The index of the result to retrieve (e.g., 0 for results[0], -1 for the last result).
            """
        )
        @limit_cost(max_cost=0)
        def get_full_result_wrapper(result_index: int, **kwargs):
            return get_full_result(result_index, self.available_results, **kwargs)

        spells_at_disposal = spells_at_disposal.copy()
        spells_at_disposal.append(done)
        spells_at_disposal.append(get_full_result_wrapper)
        self.spells_at_disposal = spells_at_disposal
        self.system_message = system_message
        self.context = context
        self.available_results = available_results
        self.max_context_window_size = max_context_window_size

    def step(
        self, 
        user_input: str | None = None
    ) -> Iterator[Any]:
        if (user_input is not None):
            self.context.append({'role': 'user', 'content': user_input})
        # Ask for the spell to cast
        spell_question = (
            'Which spell will you cast? Respond with ONLY the spell name, nothing else. '
            'No explanations, no sentences, just the exact spell name from the list. '
            'Example valid responses: "stable_diffusion" or "text_response" or "done"'
        )
        self.context.append({'role': 'system', 'content': spell_question})

        # Get the spell name from the model
        if len(self.context) > self.max_context_window_size:
            self.context[:] = self.context[-self.max_context_window_size:]
        spell_response_stream = self.brain.cast(
            model="gpt-4o-mini",
            context=self.context,
            system=self.system_description,
            max_input_tokens=30000,
            max_output_tokens=4096,
        )

        spell_response = ''
        for chunk in spell_response_stream:
            if isinstance(chunk, str):
                spell_response += chunk

        # Update context with the assistant's response
        self.context.append({'role': 'assistant', 'content': spell_response.strip()})
        raw_spell_response = spell_response.strip()

        # The model might return "spell_name: {args}", so we parse it.
        if ":" in raw_spell_response:
            spell_name = raw_spell_response.split(":", 1)[0].strip()
        else:
            spell_name = raw_spell_response
        
        # Handle generation as a special case
        if spell_name == 'generate':
            yield {"spell_name": "generate"}
            prompt_q = "What is the prompt for the text generation?"
            self.context.append({'role': 'system', 'content': prompt_q})
            
            prompt_response_stream = self.brain.cast(
                model="gpt-4o-mini",
                context=self.context,
                system=self.system_description
            )
            prompt_response = ""
            for chunk in prompt_response_stream:
                if isinstance(chunk, str):
                    prompt_response += chunk
            self.context.append({'role': 'assistant', 'content': prompt_response})
            yield {"spell_args": f"prompt={prompt_response}"}

            generation_stream = self.brain.cast(
                system="You are a helpful assistant.",
                context=[{'role': 'user', 'content': prompt_response}]
            )
            generation_result = ""
            for chunk in generation_stream:
                if isinstance(chunk, str):
                    generation_result += chunk
            
            self.available_results.append(generation_result)
            yield generation_result
            return

        yield {"spell_name": spell_name}

        # Validate the spell name
        spell_names_at_disposal = [spell.__name__ for spell in self.spells_at_disposal]
        if spell_name not in spell_names_at_disposal:
            err = f"Unknown spell: {spell_name}. Please try again."
            yield {"error": err}
            self.context.append({'role': 'system', 'content': err})
            return

        # Ask for the arguments to pass to the spell
        args_question = (
            'What arguments will you pass to the spell? Provide ONLY the arguments in this exact format:\n'
            'key1=value1\n'
            'key2=value2\n'
            'Each argument on a new line. No explanations or extra text. '
            'To reference previous results: use results[N] for entire values or {results[N]} inside strings. '
            'Example: "input=A detailed photo of a dog" or "command=ls -lh {results[0]}"'
        )
        self.context.append({'role': 'system', 'content': args_question})

        # Get the arguments from the model
        args_response_stream = self.brain.cast(
            model="gpt-4o-mini",
            context=self.context,
            system=self.system_description,
            max_input_tokens=30000,
            max_output_tokens=4096,
        )

        args_response = ''
        for chunk in args_response_stream:
            if isinstance(chunk, str):
                args_response += chunk
                yield {"spell_args_chunk": chunk}


        # Update context with the assistant's response
        self.context.append({'role': 'assistant', 'content': args_response.strip()})
        spell_args = args_response.strip()
        yield {"spell_args": spell_args}

        # Run the selected spell with the provided arguments
        spell_to_cast = next(spell for spell in self.spells_at_disposal if spell.__name__ == spell_name)

        # clear then set the next spell to cast
        self.magic.spells = []
        self.magic.add(spell_to_cast)
        SpellArgsModel = create_pydantic_model_from_function(spell_to_cast)
        
        required_fields = [
            f for f, model_field in SpellArgsModel.model_fields.items() if model_field.is_required()
        ]

        if not spell_args.strip() and required_fields:
            err = f"The '{spell_name}' spell requires arguments, but none were provided. Required: {', '.join(required_fields)}"
            yield {"error": err}
            self.context.append({'role': 'system', 'content': err})
            return

        # Parse user input into a dictionary
        try:
            import re
            input_data = {}
            for line in spell_args.strip().splitlines():
                if '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip()

                    # Check if entire value is a result reference (e.g., "results[5]")
                    if value.startswith('results[') and value.endswith(']'):
                        index_str = value[8:-1]
                        try:
                            index = int(index_str)
                            if 0 <= index < len(self.available_results):
                                input_data[key.strip()] = self.available_results[index]
                            else:
                                raise ValueError(f"Result index {index} out of range.")
                        except (ValueError, IndexError):
                            raise ValueError(f"Invalid result index: {index_str}")
                    else:
                        # Check if value contains result references in template form (e.g., "ls -lh {results[5]}")
                        def replace_result_refs(match):
                            index_str = match.group(1)
                            try:
                                index = int(index_str)
                                if 0 <= index < len(self.available_results):
                                    return str(self.available_results[index])
                                else:
                                    raise ValueError(f"Result index {index} out of range.")
                            except (ValueError, IndexError):
                                raise ValueError(f"Invalid result index: {index_str}")

                        # Replace {results[N]} with actual values
                        value = re.sub(r'\{results\[(\d+)\]\}', replace_result_refs, value)
                        input_data[key.strip()] = value
        except ValueError as e:
            err = f"Invalid argument format or result index: {e}"
            yield {"error": err}
            self.context.append({'role': 'system', 'content': err})
            return

        # Validate and parse the input using the dynamic Pydantic model
        parsed_args = {}
        try:
            parsed_args = SpellArgsModel(**input_data).model_dump(exclude_unset=True)
            # Call the spell function with parsed arguments
        except ValidationError as e:
            err = f"Validation error: {e}"
            yield {"error": err}
            self.context.append({'role': 'system', 'content': err})
            return

        # Cast the spell
        output_stream = self.magic.cast(**parsed_args)

        # Process and display the output
        spell_results = []
        for output in output_stream:
            self.available_results.append(output)
            spell_results.append(output)
            yield output

        # Add the spell result to context so the agent knows what happened
        if spell_results:
            result_index = len(self.available_results) - len(spell_results)
            result_summary = f"Spell '{spell_name}' completed. Result stored at results[{result_index}]"
            if len(spell_results) == 1:
                result_str = str(spell_results[0])
                if len(result_str) <= 500:
                    result_summary += f": {result_str}"
                else:
                    result_summary += f": {result_str[:500]}... (+{len(result_str)-500} characters, use get_full_result_wrapper to see full content)"
            self.context.append({'role': 'system', 'content': result_summary})

    @property
    def system_description(self) -> str:
        results_info = ""
        if self.available_results:
            results_info = "\n\nAvailable results from previous spells:\n"
            for i, result in enumerate(self.available_results):
                result_str = str(result)
                if len(result_str) > 2000:
                    truncated = len(result_str) - 2000
                    results_info += f"  - results[{i}]: {result_str[:2000]}... (+{truncated} characters truncated)\n"
                else:
                    results_info += f"  - results[{i}]: {result_str}\n"

        return (
            f"{self.system_message}\nAvailable spells:\n{self.spell_info}{results_info}"
        )

    @property
    def spell_info(self) -> str:
        spell_descriptions = [
            f"{spell.__name__}: {spell.agent_hint if hasattr(spell, 'agent_hint') else spell.__doc__}"
            for spell in self.spells_at_disposal
        ]
        generate_description = "generate: Generates text using the language model. Useful for creating content, writing code, or answering questions."
        spell_descriptions.append(generate_description)
        return "\n".join(spell_descriptions)


@limit_cost(max_cost=lambda max_cost_per_brain_cast: max_cost_per_brain_cast)
def agent(
    user_input: str | None,
    brain_spell: Callable,
    spells_at_disposal: list[Callable],
    context: list[dict] = [],
    available_results: list[Any] = [],
    system_message: str = (
        "You are a helpful and intelligent agent that uses spells to fulfill user requests. "
        "Choose a spell and provide the necessary arguments. Only one spell can be cast at a time. "
        "Continue casting spells until the task is complete. "
        "Respond concisely and only with the requested information. "
        "Do not include additional commentary. If you need to comment or ask a question, "
        "use a text_response or speech_response. "
        "In each response, you will be asked to provide either a spell name or arguments to a spell. "
        "Only provide one but not both at the same time. Do not provide done=True as an argument. It should "
        "only be cast as a spell."
    ),
    max_context_window_size: int = 100,
    max_cost_per_brain_cast: float = 6.5,
    max_cost_per_spell_cast: float = 6.5,
) -> Iterator[tuple[Union[dict[str, str], bool, str, Any], list[dict]]]:
    a = Agent(
        brain_spell,
        spells_at_disposal,
        system_message,
        context,
        available_results,
        max_context_window_size,
        max_cost_per_brain_cast,
        max_cost_per_spell_cast,
    )

    while True:
        outputs = a.step(user_input)
        user_input = None

        has_finished = False
        for output in outputs:
            if isinstance(output, bool):
                has_finished = True
            yield output, a.context
        
        if has_finished:
            break


spells = [agent]
