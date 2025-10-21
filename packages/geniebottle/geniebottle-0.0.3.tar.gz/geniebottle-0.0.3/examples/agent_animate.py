from geniebottle import Magic
from geniebottle.spellbooks import Local, OpenAI, StabilityAI, Agent
from rich.prompt import Prompt
from rich import print

magic = Magic(max_cost_per_cast=0.35)

spellbook = Agent()

magic.add(spellbook.get('LLMAgent'))

role = (
    'An inspired artist that is very talented and refers to a critic for '
    'feedback'
)
print(f'My role is: {role}. Chat with me to get started!')

memory = None
results = None
while True:
    input = Prompt.ask('💬')
    out = magic.cast(
        input=input,
        memory=memory,
        results=results,
        spells_at_disposal=[
            Local().get('text_response'),
            Local().get('save_content'),
            StabilityAI().get('stable_diffusion'),
            OpenAI().get('chatgpt'),
            StabilityAI().get('stable_video_diffusion')
        ],
        role=role,
        brain=OpenAI().get('chatgpt', model='gpt-4o'),
    )
    memory = out[0]['memory']
    results = out[0]['results']
