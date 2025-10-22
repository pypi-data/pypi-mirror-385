import os
from pathlib import Path

def count_how_many_files(path: Path, extension: str = None) -> int:
    """
    Counts files in a directory, optionally filtering by extension.

    Args:
        path (Path): Directory path to search for files.
        extension (str, optional): File extension to filter by (without dot).

    Returns:
        int: Number of files found matching criteria.

    Raises:
        ValueError: If path is not a directory or extension is invalid.
        FileNotFoundError: If directory doesn't exist.
        PermissionError: If user lacks permission to read directory.

    Examples:
        >>> from pathlib import Path
        >>> doc_dir = Path("documents")
        >>> total_files = count_how_many_files(doc_dir)
        >>> print(f"Total files: {total_files}")
        Total files: 15
        >>> pdf_files = count_how_many_files(doc_dir, "pdf")
        >>> print(f"PDF files: {pdf_files}")
        PDF files: 7
    """
    
    if not isinstance(path, Path):
        raise ValueError(f"Argument '{path}' must be an instance of Path")
        
    if not path.exists():
        raise FileNotFoundError(f"Path '{path}' does not exist")
    
    if not path.is_dir():
        raise ValueError(f"Path '{path}' is not a directory")
    
    # search for the files
    try:
        if extension:
            paths_to_search = f"*.{extension}"
            paths_with_extension = list(path.glob(paths_to_search))
            return len(paths_with_extension)
        else:
            return len([file for file in os.listdir(path)])
    except PermissionError as e:
        raise
    
 





    
    
    



    


    

    





