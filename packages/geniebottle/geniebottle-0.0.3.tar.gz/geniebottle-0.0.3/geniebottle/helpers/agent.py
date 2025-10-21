from PIL import Image
from io import BytesIO
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def display_output_locally(output):
    if isinstance(output, str):
        console.print(Panel(output, title="[bold green]Agent Response[/bold green]", expand=False))
    elif isinstance(output, list):
        text = Text()
        for item in output:
            text.append(f"• {item}\n")
        console.print(Panel(text, title="[bold blue]File List[/bold blue]", expand=False))
    elif isinstance(output, dict):
        if "spell_name" in output:
            console.print(Panel(output['spell_name'], title="[bold magenta]Casting Spell[/bold magenta]", expand=False))
        elif "spell_args" in output:
            console.print(Panel(output['spell_args'], title="[bold cyan]With Arguments[/bold cyan]", expand=False))
        elif "error" in output:
            console.print(Panel(output['error'], title="[bold red]Error[/bold red]", expand=False))
    elif isinstance(output, (Image.Image, BytesIO)):
        if isinstance(output, BytesIO):
            output = Image.open(output)
        output.show()
    elif isinstance(output, bool):
        if output:
            console.print("[bold green]✓ Task complete[/bold green]")
        else:
            console.print("[bold red]✗ Task failed[/bold red]")
    else:
        console.print(Panel(str(output), title="[bold yellow]Debug Output[/bold yellow]", expand=False))
    return output
