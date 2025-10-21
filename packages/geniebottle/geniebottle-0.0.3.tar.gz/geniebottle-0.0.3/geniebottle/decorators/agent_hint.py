from functools import wraps


def agent_hint(hint: str, allowed_kwargs: list = None) -> callable:
    """
    A decorator to apply to spells to give an agent hints about what arguments to
    use and how to use them. It is useful if this differs from the spell's docstring.

    Example:
        @agent_hint(
            '''
                Chat with ChatGPT from OpenAI.

                Args:
                    input (Union[str, None], optional): The input to the model. It is best to use conversational language. Defaults to None.
                    context (Union[str, list[dict[str, str]], None], optional): The context to the model. Defaults to None.
                    system (str, optional): The system prompt to the model. Defaults to 'You are a helpful assistant.'.

                Returns:
                    str: The response from the model.
            ''',
            allowed_kwargs=['input', 'context', 'system']
        )
        def spell(input, context, system):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, 'agent_hint', hint)
        setattr(wrapper, 'agent_allowed_kwargs', allowed_kwargs)

        return wrapper

    return decorator
