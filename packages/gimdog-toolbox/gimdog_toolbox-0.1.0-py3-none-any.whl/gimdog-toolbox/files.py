"""
Created in 2025 July

@author: Aron Gimesi (https://github.com/gimesia)
@contact: gimesiaron@gmail.com
"""

import os
import re


def get_all_filepaths(directory, extensions=None):
    """
    Recursively retrieves all file paths from the specified directory, optionally filtering by file extensions.

    Args:
        directory (str): The root directory to search for files.
        extensions (list or tuple, optional): A list or tuple of file extensions to filter by (e.g., ['.txt', '.csv']).
            If None, all files are returned.

    Returns:
        list: A list of full file paths matching the specified extensions (or all files if extensions is None).
    """
    filepaths = []
    for root, dirs, files in os.walk(directory):
        filepaths.extend(os.path.join(root, file) for file in files if extensions is None or file.endswith(tuple(extensions)))
    return filepaths


def get_first_level_subdirectories(directory):
    """
    Get the first-level subdirectories in a directory.

    Args:
        directory (str): The directory to search for subdirectories.

    Returns:
        list of str: List of first-level subdirectory paths.
    """
    subdirectories = []
    subdirectories.extend(entry.path for entry in os.scandir(directory) if entry.is_dir())
    return subdirectories


def get_all_subdirectories(directory):
    """
    Get all subdirectories in a directory.

    Args:
        directory (str): The directory to search for subdirectories.

    Returns:
        list of str: List of all subdirectory paths.
    """
    subdirectories = []
    for root, dirs, files in os.walk(directory):
        subdirectories.extend(os.path.join(root, dir) for dir in dirs)
    return subdirectories


def remove_string_from_filenames_in_directory(directory, removed_string):
    """
    Removes a specified substring from all filenames in a given directory.

    Iterates through the files in the specified directory and renames each file
    by removing the provided substring from its filename.

    Args:
        directory (str): The path to the directory containing the files to rename.
        removed_string (str): The substring to remove from each filename.

    Raises:
        FileNotFoundError: If the specified directory does not exist.
        PermissionError: If the process lacks permissions to rename files.
        OSError: If an error occurs during renaming.
    """
    for filename in os.listdir(directory):
        if removed_string in filename:
            new_filename = filename.replace(removed_string, "")
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))


def remove_files_by_pattern(directory, pattern):
    """
    Walk through a directory and its subdirectories, and remove files that match the given pattern.

    Args:
    directory (str): The root directory to start the search.
    pattern (str): The regex pattern to match the filenames.

    Returns:
    None
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if re.match(pattern, file):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Removed file: {file_path}")


# Example usage:
# pattern = r'.*\.png$'
# remove_files_by_pattern('/path/to/directory', pattern)
