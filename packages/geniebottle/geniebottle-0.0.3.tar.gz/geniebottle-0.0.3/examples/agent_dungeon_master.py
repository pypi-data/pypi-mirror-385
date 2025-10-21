# Parts of the example system prompt are derived from material taken from the System Reference Document 5.1 ("SRD 5.1")
# by Wizards of the Coast LLC and available at https://dnd.wizards.com/resources/systems-reference-document. The SRD 5.1
# is licensed under the Creative Commons Attribution 4.0 International License available at https://creativecommons.org/licenses/by/4.0/legalcode.
# The rest of the code related to AI and the `magic` library are licensed under the MPL (see the LICENSE file).

from geniebottle.spellbooks import OpenAI, StabilityAI, Local, Agent, File
from geniebottle.scrolls import AgentScroll
from geniebottle import Magic

# Create scroll
scroll = AgentScroll()

# Create Magic instance at module level for serving
magic = Magic(max_cost_per_cast=5)
magic.add(Agent().get('agent'))

def main():
    context = []

    # Custom welcome for dungeon master
    scroll.console.print("\n")
    scroll.console.print("🐉 [bold cyan]Welcome to the Dungeon Master Agent![/bold cyan]")
    scroll.console.print()
    scroll.console.print("[dim]An AI-powered Dungeons & Dragons game master[/dim]")
    scroll.console.print("[dim]The DM will generate images for new areas and characters[/dim]")
    scroll.console.print()

    # Default DnD 5e system prompt
    default_system = (
        'You are a dungeon master that runs the user through a dungeons and dragons game. '
        'The user can interact with the game by making choices and the dungeon master will respond accordingly. '
        'Every time the user enters a new area or sees a new character, the dungeon master will '
        'generate a new image of the area or character using stable_diffusion or dalle. '
        'The dungeon master will also generate a new image when the user makes a '
        'choice that affects the story. Every time an image is generated, '
        'save it using save_content. The DM will also roll dice for the user to decide '
        'the outcome of certain events, following DnD 5e rules. '
        'Use text_response to narrate the story and describe what happens. '
        'Once you have fully completed responding to the user, cast the done spell with done=true.'
    )

    scroll.inscribe('🎲', 'Enter a custom system prompt (or press enter for default DnD 5e DM):')
    system = input()
    if not system.strip():
        system = default_system

    while True:
        try:
            # Get user input
            scroll.inscribe("💬", "")
            user_input = input()

            if user_input.lower() in ['exit', 'quit']:
                break

            # Cast spells through the agent
            outputs = magic.cast(
                user_input=user_input,
                brain_spell=OpenAI().get('chatgpt'),
                max_cost_per_brain_cast=5.0,
                spells_at_disposal=[
                    StabilityAI().get('stable_diffusion'),
                    OpenAI().get('dalle'),
                    Local().get('text_response'),
                    Local().get('speech_response'),
                    Local().get('save_content'),
                    Local().get('open_image'),
                    Local().get('random_number'),
                    File().get('read_file'),
                    File().get('write_file'),
                ],
                context=context,
                system_message=system,
            )

            skip_done_spell = False
            current_spell_name = None
            available_results = []

            for output, new_context in outputs:
                context = new_context

                if isinstance(output, dict):
                    if "spell_name" in output:
                        if output['spell_name'] == 'done':
                            skip_done_spell = True
                            continue
                        skip_done_spell = False
                        current_spell_name = output['spell_name']
                        scroll.cast_spell(output['spell_name'], show_args=True)
                    elif "spell_args_chunk" in output:
                        if skip_done_spell:
                            continue
                        scroll.stream_args(output['spell_args_chunk'])
                    elif "error" in output:
                        scroll.show_error(output['error'])

                elif isinstance(output, str):
                    available_results.append(output)
                    scroll.reveal(output)
                elif isinstance(output, list):
                    available_results.append(output)
                    scroll.reveal(output)
                elif isinstance(output, bool) and output:
                    # Task completed
                    if not skip_done_spell and current_spell_name:
                        if scroll._animation_active:
                            scroll._stop_animation()
                    skip_done_spell = False
                    current_spell_name = None
                elif isinstance(output, bool) and not output:
                    scroll.show_error("Task failed")
                else:
                    available_results.append(output)
                    scroll.reveal(str(output))

        except KeyboardInterrupt:
            scroll.inscribe("❌", "Exiting dungeon...")
            break
        except EOFError:
            scroll.inscribe("❌", "Exiting dungeon...")
            break

if __name__ == "__main__":
    main()
