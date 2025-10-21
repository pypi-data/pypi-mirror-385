from geniebottle.decorators import agent_hint, limit_cost
import os
import re
import subprocess

@agent_hint(
    """Read the content of a file.

    Args:
        file_path (str): The path to the file to read.
    """
)
@limit_cost(max_cost=0)
def read_file(file_path: str, **kwargs):
    """A spell that reads the content of a file.

    Args:
        file_path (str): The path to the file to read.
    """
    cleaned_path = file_path.strip('\'"')
    cleaned_path = os.path.expanduser(cleaned_path)
    with open(cleaned_path, 'r') as file:
        return file.read()


@agent_hint(
    """Write content to a file. This will overwrite the file if it already exists.

    Args:
        file_path (str): The path to the file to write to.
        content (str): The content to write to the file.
    """
)
@limit_cost(max_cost=0)
def write_file(file_path: str, content: str, **kwargs):
    """A spell that writes content to a file.

    This will overwrite the file if it already exists.

    Args:
        file_path (str): The path to the file to write to.
        content (str): The content to write to the file.
    """
    cleaned_path = file_path.strip('\'"')
    cleaned_path = os.path.expanduser(cleaned_path)
    with open(cleaned_path, 'w') as file:
        file.write(content)
    return f"Content written to {cleaned_path}"


@agent_hint(
    """Edit a file by replacing a specific string with new content.

    Args:
        file_path (str): The path to the file to edit.
        old_content (str): The content to be replaced.
        new_content (str): The new content to insert.
    """
)
@limit_cost(max_cost=0)
def edit_file(file_path: str, old_content: str, new_content: str, **kwargs):
    """A spell that edits a file by replacing a specific string with new content.

    Args:
        file_path (str): The path to the file to edit.
        old_content (str): The content to be replaced.
        new_content (str): The new content to insert.
    """
    cleaned_path = file_path.strip('\'"')
    cleaned_path = os.path.expanduser(cleaned_path)
    with open(cleaned_path, 'r') as file:
        file_content = file.read()

    new_file_content = file_content.replace(old_content, new_content)

    with open(cleaned_path, 'w') as file:
        file.write(new_file_content)

    return f"File {cleaned_path} edited successfully."

@agent_hint(
    """List all files in a directory.

    Args:
        directory (str): The path to the directory to list files from.
    """
)
@limit_cost(max_cost=0)
def list_files(directory: str, **kwargs):
    """A spell that lists all files in a directory.

    Args:
        directory (str): The path to the directory to list files from.
    """
    directory = os.path.expanduser(directory)
    return os.listdir(directory)


@agent_hint(
    """Delete a file.

    Args:
        file_path (str): The path to the file to delete.
    """
)
@limit_cost(max_cost=0)
def delete_file(file_path: str, **kwargs):
    """A spell that deletes a file.

    Args:
        file_path (str): The path to the file to delete.
    """
    os.remove(file_path)
    return f"File {file_path} deleted successfully."


@agent_hint(
    """Find a file in the current project.

    Args:
        query (str): The file name or part of the file name to search for.
        directory (str): The directory to search in. Defaults to current directory.
    """
)
@limit_cost(max_cost=0)
def find_file(query: str, directory: str = '.', **kwargs):
    """A spell that finds a file by its name in the current project.

    Args:
        query (str): The file name or part of the file name to search for.
        directory (str): The directory to search in. Defaults to current directory.
    """
    # Expand ~ to home directory
    directory = os.path.expanduser(directory)
    matches = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if query in file:
                matches.append(os.path.join(root, file))
    return matches


@agent_hint(
    """Search for text in files using a regular expression.

    Args:
        query (str): The regex pattern to search for.
        directory (str): The directory to search in. Defaults to current directory.
    """
)
@limit_cost(max_cost=0)
def text_search_in_files(query: str, directory: str = '.', **kwargs):
    """A spell that searches for text in files.

    Args:
        query (str): The text or regex pattern to search for.
        directory (str): The directory to search in.
    """
    # Expand ~ to home directory
    directory = os.path.expanduser(directory)
    results = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if re.search(query, line):
                            results.append(f"{file_path}:{line_num}:{line.strip()}")
            except Exception:
                # Ignore files that can't be opened, e.g. binary files
                pass
    return results


@agent_hint(
    """Run a terminal/shell command and return its output. Use this for system operations
    like checking file sizes (ls -lh), listing directories, getting file info (stat), etc.

    Args:
        command (str): The shell command to execute (e.g., 'ls -lh dog.png' to check file size).
    """
)
@limit_cost(max_cost=0)
def run_terminal_command(command: str, **kwargs):
    """A spell that runs a terminal command.

    Args:
        command (str): The command to run.
    """
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e}\n{e.stderr}"


@agent_hint(
    """Search for code in the current project. This is a simple keyword search in code files.

    Args:
        query (str): The keyword to search for in the code.
        directory (str): The directory to search in. Defaults to current directory.
    """
)
@limit_cost(max_cost=0)
def code_search(query: str, directory: str = '.', **kwargs):
    """A spell that searches for code in the current project.

    Args:
        query (str): The keyword to search for.
        directory (str): The directory to search in.
    """
    # Expand ~ to home directory
    directory = os.path.expanduser(directory)
    results = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Simple filter for common code file extensions
            if file.endswith(('.py', '.js', '.ts', '.html', '.css', '.md', '.json', '.yml', '.yaml')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if query in content:
                            results.append(file_path)
                except Exception:
                    pass
    return results


@agent_hint(
    """Move or rename a file from one location to another.

    Args:
        source (str): The path to the file to move.
        destination (str): The destination path or directory.
    """
)
@limit_cost(max_cost=0)
def move_file(source: str, destination: str, **kwargs):
    """A spell that moves or renames a file.

    Args:
        source (str): The path to the file to move.
        destination (str): The destination path.
    """
    import shutil
    try:
        # If destination is a directory, move file into it with same name
        if os.path.isdir(destination):
            file_name = os.path.basename(source)
            destination = os.path.join(destination, file_name)

        shutil.move(source, destination)
        return f"Moved {source} to {destination}"
    except Exception as e:
        return f"Error moving file: {e}"


@agent_hint(
    """Copy a file from one location to another.

    Args:
        source (str): The path to the file to copy.
        destination (str): The destination path or directory.
    """
)
@limit_cost(max_cost=0)
def copy_file(source: str, destination: str, **kwargs):
    """A spell that copies a file.

    Args:
        source (str): The path to the file to copy.
        destination (str): The destination path.
    """
    import shutil
    try:
        # If destination is a directory, copy file into it with same name
        if os.path.isdir(destination):
            file_name = os.path.basename(source)
            destination = os.path.join(destination, file_name)

        shutil.copy2(source, destination)
        return f"Copied {source} to {destination}"
    except Exception as e:
        return f"Error copying file: {e}"


spells = (read_file, write_file, edit_file, list_files, delete_file, find_file, text_search_in_files, run_terminal_command, code_search, move_file, copy_file)
