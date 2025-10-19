import os
import win32com.client

SYNOLOGY_SYSTEM_FOLDER = os.path.join(
    os.path.expanduser("~"), "AppData", "Local", "SynologyDrive", "SystemFolders"
)


def _get_shortcut_target(path: os.PathLike) -> os.PathLike:
    """
    Extracts the target path of a shortcut file.

    Args:
        path (os.PathLike): Path to the shortcut file.

    Returns:
        os.PathLike: Path of the shortcuts target.
    """
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(path)
    return shortcut.Targetpath


def _raise_synology_system_folder_not_found():
    """
    Raises:
        FileNotFoundError: Raises FileNotFoundError if the Synology Drive System Folder is not found.
    """
    raise FileNotFoundError("Synology Drive System Folder not found")


def get_synology_nas() -> list[os.PathLike]:
    """
    Get all Synology NAS in the Synology Drive System Folder.

    Returns:
        list[os.PathLike]: List of all Synology NAS paths in the Synology Drive System Folder.
    """
    # Check if the Synology Drive Client System Folder exists
    if not os.path.isdir(SYNOLOGY_SYSTEM_FOLDER):
        _raise_synology_system_folder_not_found()

    # Get synology NAS systems
    synology_nas_indices = os.listdir(SYNOLOGY_SYSTEM_FOLDER)
    return [
        os.path.join(SYNOLOGY_SYSTEM_FOLDER, synology_nas_index)
        for synology_nas_index in synology_nas_indices
    ]


def get_server_paths() -> dict[str, dict[str, os.PathLike]]:
    """
    Returns all available server paths in a dictionary with their respective NAS index and shortcut name.

    Returns:
        dict[str, dict[str, os.PathLike]]: Returns all available server paths in a
        dictionary with their respective NAS index and shortcut name.

        Example: datasets = server_paths["1"]["datasets"]
    """
    # Check if the Synology Drive Client System Folder exists
    if not os.path.isdir(SYNOLOGY_SYSTEM_FOLDER):
        raise _raise_synology_system_folder_not_found()

    # Get all connected Synology NAS systems
    nas_systems = get_synology_nas()

    server_paths = {}
    # Loop through all NAS systems and get all shortcuts
    for nas_system in nas_systems:
        nas_index = nas_system.split("\\")[-1]
        server_paths[nas_index] = {}
        nas_contents = os.listdir(nas_system)
        # Loop through all shortcuts and get their target
        for shortcut in nas_contents:
            shortcut_path = os.path.join(nas_system, shortcut)
            target = _get_shortcut_target(shortcut_path)
            server_paths[nas_index][target.split("\\")[-1]] = target

    return server_paths
