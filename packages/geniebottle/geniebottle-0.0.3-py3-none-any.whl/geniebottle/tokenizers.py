import tiktoken


def tiktoken_tokenize(model='gpt-4'):
    enc = tiktoken.encoding_for_model(model)

    def tokenize(text):
        ''' An OpenAI tokeniser

        See https://platform.openai.com/tokenizer
        for more info
        '''
        return enc.encode(text)

    return tokenize
