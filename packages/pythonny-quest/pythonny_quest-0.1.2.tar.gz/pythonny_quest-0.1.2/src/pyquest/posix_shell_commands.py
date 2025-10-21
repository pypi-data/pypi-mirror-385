"""
POSIX-compliant shell commands module.

This module provides basic implementations of pwd and cd commands
that work consistently across Windows, Linux, and Mac platforms,
always outputting POSIX-compliant paths with forward slashes.
"""

import os
from pathlib import Path
import stat


def pwd():
    """
    Print working directory - returns the current working directory path.
    
    Returns:
        str: Current working directory path with POSIX-style forward slashes
        
    Example:
        >>> pwd()
        '/home/user/documents'  # On Linux/Mac
        '/c/Users/user/documents'  # On Windows (converted to POSIX style)
    """
    current_dir = Path.cwd()
    
    # Convert to POSIX-style path string
    posix_path = current_dir.as_posix()
    
    # On Windows, convert drive letters to POSIX format (C: -> /c)
    if os.name == 'nt' and len(posix_path) >= 2 and posix_path[1] == ':':
        drive_letter = posix_path[0].lower()
        posix_path = f'/{drive_letter}{posix_path[2:]}'
    
    return posix_path


def cd(path=None):
    """
    Change directory - changes the current working directory.
    
    Args:
        path (str, optional): Target directory path. If None or empty,
                            changes to user's home directory.
                            Supports both POSIX and native path formats.
    
    Returns:
        str: New current working directory path with POSIX-style forward slashes
        
    Raises:
        FileNotFoundError: If the specified directory doesn't exist
        NotADirectoryError: If the specified path is not a directory
        PermissionError: If access to the directory is denied
        
    Examples:
        >>> cd('/home/user/documents')
        '/home/user/documents'
        
        >>> cd('subfolder')
        '/home/user/documents/subfolder'
        
        >>> cd('..')
        '/home/user'
        
        >>> cd()  # Go to home directory
        '/home/user'
        
        >>> cd('C:\\Users\\user')  # Windows path on Windows
        '/c/Users/user'
    """
    if path is None or path == '':
        # Change to home directory
        target_path = Path.home()
    else:
        # Handle POSIX-style paths on Windows
        if os.name == 'nt' and path.startswith('/') and len(path) >= 2:
            # Convert POSIX-style path to Windows format if needed
            # e.g., '/c/Users/user' -> 'C:/Users/user'
            if path[1:2].isalpha() and (len(path) == 2 or path[2] == '/'):
                drive_letter = path[1].upper()
                path = f'{drive_letter}:{path[2:]}'
        
        target_path = Path(path).resolve()
    
    # Verify the target exists and is a directory
    if not target_path.exists():
        raise FileNotFoundError(f"Directory not found: {path}")
    
    if not target_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {path}")
    
    # Change to the directory
    os.chdir(target_path)
    
    # Return the new current directory in POSIX format
    return pwd()


def ls(path=None):
    """
    List directory contents - lists files and directories in the specified path.
    
    Args:
        path (str, optional): Directory path to list. If None, lists current
                            working directory. Supports both POSIX and native
                            path formats.
    
    Returns:
        list: List of dictionaries containing file/directory information.
              Each dictionary contains:
              - 'name': filename/directory name
              - 'type': 'file', 'directory', or 'other'
              - 'path': full POSIX-style path
              - 'size': file size in bytes (0 for directories)
              - 'permissions': permission string (e.g., 'rwxr-xr-x')
        
    Raises:
        FileNotFoundError: If the specified directory doesn't exist
        NotADirectoryError: If the specified path is not a directory
        PermissionError: If access to the directory is denied
        
    Examples:
        >>> ls()  # List current directory
        [{'name': 'file.txt', 'type': 'file', 'path': '/home/user/file.txt', 
          'size': 1024, 'permissions': 'rw-r--r--'}, ...]
        
        >>> ls('/home/user/documents')
        [{'name': 'doc.pdf', 'type': 'file', 'path': '/home/user/documents/doc.pdf',
          'size': 2048, 'permissions': 'rw-r--r--'}, ...]
        
        >>> ls('C:\\Users\\user')  # Windows path
        [{'name': 'Desktop', 'type': 'directory', 'path': '/c/Users/user/Desktop',
          'size': 0, 'permissions': 'rwxr-xr-x'}, ...]
    """
    if path is None:
        target_path = Path.cwd()
    else:
        # Handle POSIX-style paths on Windows (same logic as cd function)
        if os.name == 'nt' and path.startswith('/') and len(path) >= 2:
            if path[1:2].isalpha() and (len(path) == 2 or path[2] == '/'):
                drive_letter = path[1].upper()
                path = f'{drive_letter}:{path[2:]}'
        
        target_path = Path(path).resolve()
    
    # Verify the target exists and is a directory
    if not target_path.exists():
        raise FileNotFoundError(f"Directory not found: {path}")
    
    if not target_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {path}")
    
    # List directory contents
    entries = []
    try:
        for entry in target_path.iterdir():
            # Get file info
            entry_stat = entry.stat()
            
            # Determine entry type
            if entry.is_file():
                entry_type = 'file'
            elif entry.is_dir():
                entry_type = 'directory'
            else:
                entry_type = 'other'  # symlinks, devices, etc.
            
            # Convert path to POSIX format
            entry_posix = entry.as_posix()
            if os.name == 'nt' and len(entry_posix) >= 2 and entry_posix[1] == ':':
                drive_letter = entry_posix[0].lower()
                entry_posix = f'/{drive_letter}{entry_posix[2:]}'
            
            # Get permissions string
            permissions = _format_permissions(entry_stat.st_mode)
            
            entries.append({
                'name': entry.name,
                'type': entry_type,
                'path': entry_posix,
                'size': entry_stat.st_size if entry.is_file() else 0,
                'permissions': permissions
            })
    
    except PermissionError:
        raise PermissionError(f"Permission denied: {target_path}")
    
    # Sort entries: directories first, then files, both alphabetically
    entries.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))
    
    return entries


def _format_permissions(mode):
    """
    Convert file mode to readable permission string.
    
    Args:
        mode (int): File mode from os.stat()
        
    Returns:
        str: Permission string like 'rwxr-xr-x'
    """
    permissions = []
    
    # Owner permissions
    permissions.append('r' if mode & stat.S_IRUSR else '-')
    permissions.append('w' if mode & stat.S_IWUSR else '-')
    permissions.append('x' if mode & stat.S_IXUSR else '-')
    
    # Group permissions
    permissions.append('r' if mode & stat.S_IRGRP else '-')
    permissions.append('w' if mode & stat.S_IWGRP else '-')
    permissions.append('x' if mode & stat.S_IXGRP else '-')
    
    # Other permissions
    permissions.append('r' if mode & stat.S_IROTH else '-')
    permissions.append('w' if mode & stat.S_IWOTH else '-')
    permissions.append('x' if mode & stat.S_IXOTH else '-')
    
    return ''.join(permissions)


# Example usage and testing
if __name__ == "__main__":
    print("Current directory:", pwd())
    
    # Example of changing to home directory
    try:
        home_dir = cd()
        print("Changed to home directory:", home_dir)
    except Exception as e:
        print(f"Error changing to home: {e}")
    
    # List current directory contents
    try:
        contents = ls()
        print(f"\nContents of {pwd()}:")
        for item in contents[:5]:  # Show first 5 items
            print(f"  {item['type']:9} {item['permissions']} {item['size']:>8} {item['name']}")
        if len(contents) > 5:
            print(f"  ... and {len(contents) - 5} more items")
    except Exception as e:
        print(f"Error listing directory: {e}")
    
    # Example of changing to a relative directory
    try:
        # This will fail if Documents doesn't exist, but demonstrates usage
        docs_dir = cd("Documents")
        print("\nChanged to Documents:", docs_dir)
        
        # List Documents directory
        docs_contents = ls()
        print("Contents of Documents:")
        for item in docs_contents[:3]:
            print(f"  {item['name']} ({item['type']})")
            
    except Exception as e:
        print(f"Error with Documents directory: {e}")
    
    # Go back to original directory
    try:
        back_dir = cd("..")
        print("\nWent back up one level:", back_dir)
    except Exception as e:
        print(f"Error going back: {e}")
    
    # Demonstrate ls with explicit path
    try:
        print("\nListing home directory explicitly:")
        home_contents = ls(cd())
        for item in home_contents[:3]:
            print(f"  {item['name']} - {item['type']} ({item['size']} bytes)")
    except Exception as e:
        print(f"Error listing home directory: {e}")"__main__":
    print("Current directory:", pwd())
    
    # Example of changing to home directory
    try:
        home_dir = cd()
        print("Changed to home directory:", home_dir)
    except Exception as e:
        print(f"Error changing to home: {e}")
    
    # Example of changing to a relative directory
    try:
        # This will fail if Documents doesn't exist, but demonstrates usage
        docs_dir = cd("Documents")
        print("Changed to Documents:", docs_dir)
    except Exception as e:
        print(f"Error changing to Documents: {e}")
    
    # Go back to original directory
    try:
        back_dir = cd("..")
        print("Went back up one level:", back_dir)
    except Exception as e:
        print(f"Error going back: {e}")
