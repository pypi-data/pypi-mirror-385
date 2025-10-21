from geniebottle import Magic
from geniebottle.spellbooks import StabilityAI, Local
from rich import print
from rich.prompt import Prompt
import uuid


# declare a new `Magic` instance
magic = Magic(max_cost_per_cast=0.020360)

# look up a spell book (an api service)
stabilityai = StabilityAI()

# add multiple spells from spell book
magic.add(stabilityai.get('stable_diffusion'))

# Interactive mode - only runs when executed directly
if __name__ == '__main__':
    # finally, use it to cast a spell
    response = magic.cast(
        input=Prompt.ask('What would you like to draw'),
        n=2,
        steps=50,
        chained=True,
        cfg_scale=8.0,
        width=1024,
        height=1024
    )

    print(response)

    for resp in response[0]:
        path = f'./gens/{uuid.uuid4()}.png'
        print(f'Saving {resp} at {path}')
        Local().get('save_content')(resp, 'image', path)
