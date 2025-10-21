from geniebottle import Magic
from geniebottle.spellbooks import StabilityAI
from rich import print
from rich.prompt import Prompt
from PIL import Image
import uuid


# declare a new `Magic` instance
magic = Magic(max_cost_per_cast=0.025000)

# look up a spell book (an api service)
spellbook = StabilityAI()

# add multiple spells from spell book
magic.add([spellbook.get('stable_video_diffusion')])

# load image
path = Prompt.ask('What is the path to the image?')
input_image = Image.open(path)

# finally, use it to cast a spell
response = magic.cast(
    input_image=input_image,
)

print(response)

with open(f'{uuid.uuid4()}.mp4', 'wb') as file:
    file.write(response[0])

# or serve it as an api
# magic.serve()
