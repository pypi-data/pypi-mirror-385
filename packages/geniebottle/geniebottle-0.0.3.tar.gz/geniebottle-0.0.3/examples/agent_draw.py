from geniebottle import Magic
from geniebottle.spellbooks import Agent, OpenAI, StabilityAI, Local
from rich.prompt import Prompt
from rich.live import Live
from rich import print


magic = Magic(max_cost_per_cast=5)

spellbook = Agent()

magic.add(spellbook.get('LLMAgent'))

role = (
    'An inspired artist that is very talented and refers to a critic for '
    'feedback'
)
print(f'My role is: {role}. Chat with me to get started!')


def callback(text):
    ''' Callback function to update the live display of the response '''
    live.update(text)


def save_callback(obj):
    ''' Callback function to save a spells response '''
    pass

memory = []
results = []
while True:
    input = Prompt.ask('💬')

    if input == 'exit':
        break

    live = Live("")
    with live:
        live.start()
        out = magic.cast(
            input=input,
            memory=memory,
            results=results,
            spells_at_disposal=[
                Local().get('text_response'),
                Local().get('speech_response'),
                Local().get('save_content'),
                StabilityAI().get('stable_diffusion'),
                OpenAI().get('chatgpt'),
            ],
            role=role,
            brain=OpenAI().get('chatgpt', model='gpt-4-1106-preview', max_input_tokens=5000),
            callback=callback,
            save_callback=save_callback
        )
        live.stop()
        memory += out[0]['memory']
        results += out[0]['results']
