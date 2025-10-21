from geniebottle import Magic
from geniebottle.spellbooks import Diffusers, Local
from rich import print
from rich.prompt import Prompt
# import matplotlib.pyplot as plt
import cv2
import numpy as np

# Declare a new `Magic` instance
magic = Magic(max_cost_per_cast=0)

# Add the diffusers video generation spell
diffusers = Diffusers()
magic.add(diffusers.get('animate_diff'))

# Function to display images with matplotlib
# def display_frame(frame, ax):
#     ax.imshow(frame)
#     plt.draw()
#     plt.pause(0.01)
#     ax.clear()
#
# # Create a figure for displaying frames
# fig, ax = plt.subplots()
# ax.axis('off')  # Turn off axis

# Prompt for user input
prompt = Prompt.ask('Enter your image prompt')

# Generate frames iteratively
while True:
    # Generate the next frame using the previous frame as context
    frames = magic.cast(
        input=prompt,
    )

    for frame_list in frames:
        if isinstance(frame_list, str):
            print(frame_list)
            continue

        for frame in frame_list:
            if isinstance(frame, str):
                print(frame)
                continue
            frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            cv2.imshow('Generated video', frame)
            cv2.waitKey(250)
            # if cv2.waitKey(250) & 0xFF == ord('q'):  # Play at 4fps (1000ms/4 = 250ms)
            # break
            # Display the frame
            # display_frame(frame, ax)
    cv2.destroyAllWindows()  # Close video window


        # Check if the user wants to continue
        # cont = Prompt.ask('Generate another frame? (y/n)')
        # if cont.lower() != 'y':
        #     break
        # new_prompt = Prompt.ask('Do you want to use a new prompt? (y/n)')
        # if new_prompt.lower() == 'y':
        #     prompt = Prompt.ask('Enter your image prompt')

plt.close(fig)
