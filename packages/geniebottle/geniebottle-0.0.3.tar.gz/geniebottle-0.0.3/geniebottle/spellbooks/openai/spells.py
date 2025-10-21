from typing import Union, Callable
from geniebottle.decorators import limit_cost, type_check, agent_hint, bind_to_spellbook
from geniebottle.tokenizers import tiktoken_tokenize
from geniebottle.spellbooks import OpenAI
from io import BytesIO


def get_openai_model_info(model):
    """ Provide costs and content lengths sourced from https://openai.com/api/pricing,
    https://platform.openai.com/playground (to get more accurate content lengths),
    and https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    (to get more accurate tokenising info).

    Because openai provides no cost or model info api endpoint, these values may change
    and should be treated as estimates only.
    """

    model_info_dict = {
        'gpt-3.5-turbo-0125': {
            'cost_per_token_input': 0.5 / 1_000_000,
            'cost_per_token_output': 1.5 / 1_000_000,
            'max_context_length': 4096,
            'additional_tokens_per_message': 4
        },
        'gpt-4': {
            'cost_per_token_input': 30 / 1_000_000,
            'cost_per_token_output': 60 / 1_000_000,
            'max_context_length': 8191,
            'additional_tokens_per_message': 4
        },
        'gpt-4o-mini-2024-07-18': {
            'cost_per_token_input': 0.15 / 1_000_000,
            'cost_per_token_output': 0.6 / 1_000_000,
            'max_context_length': 128000,
            'additional_tokens_per_message': 4
        },
        'gpt-4o-mini': {
            'cost_per_token_input': 0.15 / 1_000_000,
            'cost_per_token_output': 0.6 / 1_000_000,
            'max_context_length': 128000,
            'additional_tokens_per_message': 4
        },
        'gpt-4o-2024-08-06': {
            'cost_per_token_input': 2.5 / 1_000_000,
            'cost_per_token_output': 10 / 1_000_000,
            'max_context_length': 128000,
            'additional_tokens_per_message': 4
        },
        'gpt-4o-2024-11-20': {
            'cost_per_token_input': 2.5 / 1_000_000,
            'cost_per_token_output': 10 / 1_000_000,
            'max_context_length': 128000,
            'additional_tokens_per_message': 4
        },
        'gpt-4o': {
            'cost_per_token_input': 2.5 / 1_000_000,
            'cost_per_token_output': 10 / 1_000_000,
            'max_context_length': 128000,
            'additional_tokens_per_message': 4
        },
        'o1': {
            'cost_per_token_input': 15 / 1_000_000,
            'cost_per_token_output': 60 / 1_000_000,
            'max_context_length': 200000,
            'additional_tokens_per_message': 4
        },
        'o1-2024-12-17': {
            'cost_per_token_input': 15 / 1_000_000,
            'cost_per_token_output': 60 / 1_000_000,
            'max_context_length': 200000,
            'additional_tokens_per_message': 4
        },
        'o1-mini': {
            'cost_per_token_input': 3 / 1_000_000,
            'cost_per_token_output': 12 / 1_000_000,
            'max_context_length': 200000,
            'additional_tokens_per_message': 4
        },
    }

    if model not in model_info_dict.keys():
        raise ValueError(
            f'{model} is not a valid model. Valid models are: '
            f'{model_info_dict.keys()}'
        )

    return model_info_dict[model]


def get_token_count(text, tokenizer):
    if len(text) == 0:
        return 0
    tokenized = tokenizer(text)
    assert type(tokenized) == list, 'The output of a tokenizer but be a list of str'
    return len(tokenized)


def get_chatml_token_count(input, context, system, model):
    model_info = get_openai_model_info(model)

    tokenizer_fun = tiktoken_tokenize(model)

    num_tokens = 0
    for text in [input, context, system]:
        if text is None or text == '':
            continue

        if type(text) != list:
            num_tokens += get_token_count(text, tokenizer_fun)
            num_tokens += model_info['additional_tokens_per_message']
            continue

        for item in text:
            if type(item) == dict:
                num_tokens += get_token_count(item['content'], tokenizer_fun)
            else:
                num_tokens += get_token_count(item, tokenizer_fun)
            num_tokens += model_info['additional_tokens_per_message']

    num_tokens += 3  # every reply is primed with 3 tokens
    return num_tokens


def cost_per_token_input(input, context, system, model):
    model_info = get_openai_model_info(model)
    cost = model_info['cost_per_token_input']
    num_tokens = get_chatml_token_count(input, context, system, model)

    return num_tokens * cost


@limit_cost(
    cost_per_token_input=cost_per_token_input,
    cost_per_token_output=lambda max_output_tokens, model: get_openai_model_info(model)['cost_per_token_output'] * max_output_tokens,
    max_cost=lambda model, max_input_tokens, max_output_tokens: get_openai_model_info(model)['cost_per_token_output'] * max_output_tokens + get_openai_model_info(model)['cost_per_token_input'] * max_input_tokens,
)
@agent_hint(
    """ Use text to chat with ChatGPT from OpenAI.

    This is a seperate entity and not you or the user. This is useful if you need a
    second opinion or to ask a different model or assistant a question. Use a response
    spell function instead when talking to the user. If past conversation or additional
    context will help the query, use the `context` argument.

    Args:
        input (Union[str, None], optional): The input to the model. Use
        conversational language and provide `context` if that is needed to answer.
        Defaults to None.
        context (Union[str, list[dict[str, str]], None], optional): The context to the
        model. Use conversational Language. Defaults to None.
        system (str, optional): The system prompt to the model. Defaults to 'You are a
        helpful assistant.'.

    Returns:
        str: The text response from the model.

    Example:
        response = chatgpt(
            input='Where were you born?',
            system='You are Albert Einstein.'
        )
        chatgpt(
            input='What was your favourite discovery?',
            context=[
                {'role': 'user', 'content': 'Where were you born?'},
                {'role': 'assistant', 'content': response}
            ]
            system='You are Albert Einstein.'
        )
    """,
    allowed_kwargs=('input', 'context', 'system')
)
@type_check
@bind_to_spellbook(OpenAI)
def chatgpt(
    self,
    input: Union[str, None] = None,
    context: Union[str, list[dict[str, str]], None] = None,
    system: str = 'You are a helpful assistant.',
    model: str = 'gpt-4o',
    max_input_tokens: int = 3000,
    max_output_tokens: int = 1000,
    json_mode: bool = False,
    *args,
    **kwargs
):
    """ Chat with ChatGPT from OpenAI using text.

    Args:
        input (Union[str, None], optional): The input to the model. It is best to use
        conversational language. Defaults to None.
        context (Union[str, list[dict[str, str]], None], optional): The context to the
        model. Defaults to None.
        system (str, optional): The system prompt to the model. Defaults to 'You are a
        helpful assistant.'.
        model (str, optional): The model to use. Defaults to 'gpt-4o'.
        max_input_tokens (int, optional): The maximum number of tokens to generate.
        Defaults to 3000.
        max_output_tokens (int, optional): The maximum number of tokens to generate.
        Defaults to 1000.
        json_mode (bool, optional): Whether to return response in json (otherwise it
        will respond with 'text'. You must also instruct the model to produce JSON via a
        system or user message. Defaults to False.

    Returns:
        str: The text response from the model.
    """

    # Token count check
    num_input_tokens = get_chatml_token_count(input, context, system, model)
    if num_input_tokens > max_input_tokens:
        raise ValueError(
            f'Input tokens in args ({num_input_tokens}) exceeds max_input_tokens ({max_input_tokens})'
        )

    messages = []

    if system is not None:
        messages += [{"role": "system", "content": system}]

    if context is not None:
        if isinstance(context, str):
            messages += [{"role": "user", "content": context}]
        else:
            messages += context

    if input is not None:
        messages += [{"role": "user", "content": input}]

    response = self.client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_output_tokens,
        response_format={"type": "json_object" if json_mode else "text"},
        stream=True,
        *args,
        **kwargs
    )

    # provide streamed updates using yield
    for item in response:
        chunk = item.choices[0].delta.content
        print('pausing for testing...')

        if chunk is not None:
            yield chunk


@limit_cost(
    cost_per_request=lambda n: n * 0.02
)
@type_check
@bind_to_spellbook(OpenAI)
def dalle(
    self,
    input: str,
    n: int = 1,
    size: int = 512,
    *args,
    **kwargs
):
    response = self.client.images.generate(
        prompt=input,
        n=n,
        size=f'{size}x{size}'
    )
    return [data.url for data in response.data]


@bind_to_spellbook(OpenAI)
def whisper_speech_to_text(
    self,
    input,
    model: str = "whisper-1",
    response_format: str = "text",
    *args,
    **kwargs
):
    transcript = self.client.audio.transcriptions.create(
        model=model,
        file=input,
        response_format=response_format,
        *args,
        **kwargs
    )
    return transcript


@bind_to_spellbook(OpenAI)
def tts_text_to_speech(
    self,
    input: str,
    voice: str = "fable",
    model: str = "tts-1",
    output_format: str = "mp3",
    *args,
    **kwargs
) -> bytes:
    response = self.client.audio.speech.create(
        model=model,
        voice=voice,
        input=input,
        *args,
        **kwargs
    )

    audio_data = BytesIO(response.content)

    return audio_data


@bind_to_spellbook(OpenAI)
def chatgpt_tts_stream(
    self,
    input: Union[str, None] = None,
    context: Union[str, list[dict[str, str]], None] = None,
    system: str = 'You are a helpful assistant.',
    model: str = 'gpt-4o',
    voice: str = "alloy",
    tts_model: str = "tts-1",
    max_input_tokens: int = 3000,
    max_output_tokens: int = 1000,
    callback: Union[Callable, None] = None,
    sentence_delimiters: str = '.!?',
    min_chunk_size: int = 40,
    *args,
    **kwargs
):
    """
    Chat with ChatGPT and stream the response through TTS as audio chunks in near real-time.

    Converts text to speech sentence by sentence as they arrive from ChatGPT, providing
    much faster perceived response time.

    Args:
        input: The input text
        context: Conversation context
        system: System prompt
        model: ChatGPT model to use
        voice: TTS voice (alloy, echo, fable, onyx, nova, shimmer)
        tts_model: TTS model (tts-1 or tts-1-hd)
        max_input_tokens: Max input tokens
        max_output_tokens: Max output tokens
        callback: Optional callback function to handle audio chunks as they arrive
        sentence_delimiters: Characters that mark sentence boundaries for chunking
        min_chunk_size: Minimum characters before sending to TTS

    Yields:
        Audio chunks as bytes if no callback, otherwise the full text response
    """
    # Token count check
    num_input_tokens = get_chatml_token_count(input, context, system, model)
    if num_input_tokens > max_input_tokens:
        raise ValueError(
            f'Input tokens in args ({num_input_tokens}) exceeds max_input_tokens ({max_input_tokens})'
        )

    messages = []
    if system is not None:
        messages += [{"role": "system", "content": system}]
    if context is not None:
        if isinstance(context, str):
            messages += [{"role": "user", "content": context}]
        else:
            messages += context
    if input is not None:
        messages += [{"role": "user", "content": input}]

    # Stream the chat response
    chat_response = self.client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_output_tokens,
        stream=True,
    )

    # Collect text and convert to speech in chunks
    full_text = ""
    text_buffer = ""

    for chunk in chat_response:
        content = chunk.choices[0].delta.content
        if content:
            full_text += content
            text_buffer += content

            # Check if we have a complete sentence
            for delimiter in sentence_delimiters:
                if delimiter in text_buffer and len(text_buffer) >= min_chunk_size:
                    # Find the last sentence delimiter
                    last_delimiter_idx = max(text_buffer.rfind(d) for d in sentence_delimiters)

                    if last_delimiter_idx > 0:
                        # Extract the sentence(s) to convert
                        sentence_chunk = text_buffer[:last_delimiter_idx + 1].strip()
                        text_buffer = text_buffer[last_delimiter_idx + 1:]

                        if sentence_chunk:
                            # Convert this chunk to speech
                            tts_response = self.client.audio.speech.create(
                                model=tts_model,
                                voice=voice,
                                input=sentence_chunk,
                                response_format="mp3"
                            )

                            audio_data = tts_response.content

                            if callback:
                                callback(audio_data, is_final=False)
                            else:
                                yield audio_data
                    break

    # Handle any remaining text in buffer
    if text_buffer.strip():
        tts_response = self.client.audio.speech.create(
            model=tts_model,
            voice=voice,
            input=text_buffer.strip(),
            response_format="mp3"
        )

        audio_data = tts_response.content

        if callback:
            callback(audio_data, is_final=True)
        else:
            yield audio_data

    # Yield the full text at the end (for context tracking)
    if callback:
        yield full_text


spells = (chatgpt, dalle, whisper_speech_to_text, tts_text_to_speech, chatgpt_tts_stream)
