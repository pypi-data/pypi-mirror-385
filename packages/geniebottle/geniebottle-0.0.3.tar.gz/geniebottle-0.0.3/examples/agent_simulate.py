from geniebottle import Magic
from geniebottle.spellbooks import Local, OpenAI, StabilityAI, Agent
from rich.prompt import Prompt
from rich import print

magic = Magic(max_cost_per_cast=5.35)

spellbook = Agent()

magic.add(spellbook.get('LLMAgent'))

role = (
    'An assistant that generates simulations of people or things. Uses the `context` '
    'and `system` arguments to do so effectively with state.'
)
print(f'My role is: {role}. Chat with me to get started!')

memory = []
results = []
while True:
    input = Prompt.ask('💬')
    output = magic.cast(
        input=input,
        memory=memory,
        results=results,
        spells_at_disposal=[
            Local().get('text_response'),
            Local().get('save_content'),
            StabilityAI().get('stable_diffusion'),
            OpenAI().get('chatgpt')
        ],
        role=role,
        brain=OpenAI().get('chatgpt', model='gpt-4o'),

    )
    for part in output:
        print(part['results'])
        import ipdb; ipdb.set_trace()
        memory += part['memory']
        results += part['results']
