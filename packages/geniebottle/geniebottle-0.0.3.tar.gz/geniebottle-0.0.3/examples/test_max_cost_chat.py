from geniebottle import Magic
from geniebottle.spellbooks import OpenAI
from rich import print
from rich.prompt import Prompt
from rich.live import Live

# declare a new `magic` instance
magic = Magic(max_cost_per_cast=0.25)

# look up a spell book (an api service)
spellbook = OpenAI()

# add multiple spells from spell book
magic.add(spellbook.get('chatgpt'))

# finally, use it to cast a spell
system = Prompt.ask(
    '🤷 Who am I?',
    default='You are a helpful assistant'
)
print('Ask anything or type `exit` to quit')
context = []


def callback(text):
    ''' Callback function to update the live display of the response '''
    live.update(text)


while True:
    input_text = Prompt.ask('💬')

    if input_text == 'exit':
        break

    live = Live("")
    with live:  # Start the Live display
        live.start()
        response = magic.cast(
            input=input_text,
            context=context,
            system=system,
            model='gpt-4-1106-preview',
            callback=callback
        )
        live.stop()
        context += [{"role": "user", "content": input_text}]
        context += [{"role": "assistant", "content": response[0]}]
