from geniebottle.spellbooks import OpenAI, StabilityAI, Local, Agent, File, Editor
from geniebottle import Magic


# Create Magic instance at module level for serving
magic = Magic(max_cost_per_cast=15)

system_message = "You are an intelligent agent designed to accomplish tasks by breaking them down into a sequence of steps. At each step, you must select an appropriate spell from the list of available spells and provide the necessary arguments. You can use the results of previous spells by referencing them as 'results[N]' for entire values or '{results[N]}' for embedding in strings. Examples: 'file_path=results[5]' or 'command=ls -lh {results[5]}'. IMPORTANT: After casting a spell, check the 'Available results from previous spells' section to see its result before deciding your next action. Do not repeat the same spell if you already have its result. When you generate images, videos, or other content, ALWAYS save them using 'save_content' so the user can access them later. The save_content spell returns the absolute file path. To open/display images, use 'open_image' with the file path. Use 'read_file' only for text files, never for images. For file operations like checking size, use 'run_terminal_command' with commands like 'ls -lh {results[N]}'. When asked to look at code, use 'code_search' or 'codebase_search'. Once you have fully completed the user's request, cast the 'done' spell with 'done=true'. If you need to respond to the user with information, use 'text_response' with your answer, then cast 'done' with 'done=true'."

spell = Agent().get(
    'agent', 
    brain_spell=OpenAI().get('chatgpt'),
    max_cost_per_brain_cast=5.0,
    spells_at_disposal=[
        StabilityAI().get('stable_diffusion'),
        OpenAI().get('dalle'),
        Local().get('text_response'),
        Local().get('speech_response'),
        Local().get('save_content'),
        Local().get('open_image'),
        File().get('read_file'),
        File().get('write_file'),
        File().get('edit_file'),
        File().get('list_files'),
        File().get('delete_file'),
        File().get('move_file'),
        File().get('copy_file'),
        File().get('find_file'),
        File().get('text_search_in_files'),
        File().get('run_terminal_command'),
        File().get('code_search'),
        Editor().get('codebase_search'),
    ],
    system_message=system_message,
)

magic.add(spell)


if __name__ == "__main__":
    print('This script should be ran with the `bottle agent` command (to serve it alongside a "scroll" user interface).')
    print('Otherwise, you can run it as a FastAPI server with the `bottle serve ./examples/agent.py` command')
