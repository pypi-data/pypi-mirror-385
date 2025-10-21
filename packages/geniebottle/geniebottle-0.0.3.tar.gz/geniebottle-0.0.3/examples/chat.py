from geniebottle import Magic
from geniebottle.spellbooks import OpenAI
from geniebottle.scrolls import ChatScroll

# declare a new `magic` instance
magic = Magic(max_cost_per_cast=0.25)

# look up a spell book (an api service)
spellbook = OpenAI()

# add spells from spell book
magic.add(spellbook.get('chatgpt'))

# Interactive mode - only runs when executed directly
if __name__ == '__main__':
    # Create the chat scroll
    scroll = ChatScroll()
    scroll.unfurl()

    # Get system prompt
    scroll.inscribe('🤷', 'Who am I? (press enter for default: helpful assistant)')
    system = input()
    if not system.strip():
        system = 'You are a helpful assistant'

    context = []

    def callback(text):
        ''' Callback function to update the live display of the response '''
        live.update(text)

    while True:
        # Get user input
        scroll.inscribe('💬', '')
        input_text = input()

        if input_text == 'exit':
            break

        # Stream the response
        with scroll.stream_response() as live:
            live.start()
            response = magic.cast(
                input=input_text,
                context=context,
                system=system,
                model='gpt-4-1106-preview',
                callback=callback
            )
            live.stop()

        # Update context
        context += [{"role": "user", "content": input_text}]
        context += [{"role": "assistant", "content": response[0]}]
