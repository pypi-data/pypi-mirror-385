from geniebottle.decorators import agent_hint, limit_cost
import subprocess

@agent_hint(
    """Create a new file.

    Args:
        file_path (str): The path to the file to create.
    """
)
@limit_cost(max_cost=0)
def create_file(file_path: str, **kwargs):
    """A spell that creates a new file.

    Args:
        file_path (str): The path to the file to create.
    """
    with open(file_path, 'w') as file:
        pass
    return f"File {file_path} created successfully."


@agent_hint(
    """Search the codebase for a query.

    Args:
        query (str): The query to search for.
        directory (str): The directory to search in. Defaults to current directory.
    """
)
@limit_cost(max_cost=0)
def codebase_search(query: str, directory: str = '.', **kwargs):
    """A spell that searches the codebase.

    Args:
        query (str): The query to search for.
        directory (str): The directory to search in. Defaults to current directory.
    """
    import os
    # Expand ~ to home directory
    directory = os.path.expanduser(directory)
    try:
        # Use git grep with -C to change directory
        result = subprocess.run(f"cd '{directory}' && git grep '{query}'", shell=True, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"No results found for '{query}'"


@agent_hint(
    """Get information about a pull request.

    Args:
        pr_number (int): The pull request number.
    """
)
@limit_cost(max_cost=0)
def get_pull_request(pr_number: int, **kwargs):
    """A spell that gets information about a pull request.

    Args:
        pr_number (int): The pull request number.
    """
    try:
        # This is a placeholder for a more sophisticated git integration.
        # For now, it just uses gh pr view.
        result = subprocess.run(f"gh pr view {pr_number}", shell=True, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Could not get information for PR #{pr_number}. Make sure you have the GitHub CLI ('gh') installed and are in a git repository."

spells = (create_file, codebase_search, get_pull_request)
