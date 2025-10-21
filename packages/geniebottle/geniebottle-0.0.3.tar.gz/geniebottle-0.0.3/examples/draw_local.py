from geniebottle import Magic
from geniebottle.spellbooks import Diffusers, Local
from rich import print
from rich.prompt import Prompt
import uuid

# declare a new `Magic` instance
magic = Magic(max_cost_per_cast=0)

# add the diffusers image generation spell
diffusers = Diffusers()
magic.add(diffusers.get('text2image'))

# finally, use it to cast a spell
prompt = Prompt.ask('Enter your image prompt')
neg_prompt = Prompt.ask('Enter any negative prompts')

while True:
    response = magic.cast(
        input=prompt,
        negative_prompt=neg_prompt if neg_prompt != '' else None,
        steps=50,
        guidance_scale=7.5,
        width=1024,
        height=1024,
        num_images_per_prompt=1,
        local_file_model='StableDiffusionXL',
    )

    print(response)

    for resp in response[0]:
        path = f'./gens/{uuid.uuid4()}'
        print(f'Saving {resp} at {path}')
        Local().get('save_content')(resp, 'image', path)

    cont = Prompt.ask('Do you want to generate another image? (y/n)')
    if cont.lower() != 'y':
        break
    new_prompt = Prompt.ask('Do you want to use a new prompt? (y/n)')
    if new_prompt.lower() == 'y':
        prompt = Prompt.ask('Enter your image prompt')

    new_neg_prompt = Prompt.ask('Do you want to use a new negative prompt? (y/n)')
    if new_neg_prompt.lower() == 'y':
        neg_prompt = Prompt.ask('Enter any negative prompts')
