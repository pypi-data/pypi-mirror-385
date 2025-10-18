"""Core functionality for copying README files."""
import shutil
from pathlib import Path
from typing import Optional, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def get_embedded_readme() -> str:
    """
    Get the embedded README content (package README).
    
    Returns:
        str: The embedded README documentation
    """
    from . import __readme__
    return __readme__


def get_full_readme() -> str:
    """
    Get the full embedded README content (Ultimate Python Cheatsheet).
    
    Returns:
        str: The complete README.md content
    """
    from . import __readme_full__
    return __readme_full__


class ReadmeCopier:
    """Class to handle README file copying operations."""
    
    def __init__(self, source_path: Union[str, Path], target_path: Union[str, Path]):
        """
        Initialize the ReadmeCopier.
        
        Args:
            source_path: Path to the source README file
            target_path: Path to the target directory where README should be copied
        """
        self.source_path = Path(source_path)
        self.target_path = Path(target_path)
        
    def validate_source(self) -> bool:
        """
        Validate that the source README file exists.
        
        Returns:
            bool: True if source file exists, False otherwise
        """
        if not self.source_path.exists():
            logger.error(f"Source file does not exist: {self.source_path}")
            return False
        
        if not self.source_path.is_file():
            logger.error(f"Source path is not a file: {self.source_path}")
            return False
        
        return True
    
    def validate_target(self) -> bool:
        """
        Validate that the target directory exists or can be created.
        
        Returns:
            bool: True if target directory exists or was created, False otherwise
        """
        if not self.target_path.exists():
            try:
                self.target_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created target directory: {self.target_path}")
            except Exception as e:
                logger.error(f"Failed to create target directory: {e}")
                return False
        
        if not self.target_path.is_dir():
            logger.error(f"Target path is not a directory: {self.target_path}")
            return False
        
        return True
    
    def copy(self, overwrite: bool = False, rename: Optional[str] = None) -> bool:
        """
        Copy the README file to the target directory.
        
        Args:
            overwrite: If True, overwrite existing file in target directory
            rename: Optional new name for the copied file
            
        Returns:
            bool: True if copy was successful, False otherwise
        """
        if not self.validate_source():
            return False
        
        if not self.validate_target():
            return False
        
        # Determine target file name
        target_filename = rename if rename else self.source_path.name
        target_file = self.target_path / target_filename
        
        # Check if file already exists
        if target_file.exists() and not overwrite:
            logger.warning(f"Target file already exists: {target_file}")
            logger.warning("Use overwrite=True to replace it")
            return False
        
        try:
            shutil.copy2(self.source_path, target_file)
            logger.info(f"Successfully copied {self.source_path} to {target_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to copy file: {e}")
            return False
    
    def get_info(self) -> dict:
        """
        Get information about the source and target paths.
        
        Returns:
            dict: Dictionary containing path information
        """
        info = {
            "source_path": str(self.source_path.absolute()),
            "source_exists": self.source_path.exists(),
            "target_path": str(self.target_path.absolute()),
            "target_exists": self.target_path.exists(),
        }
        
        if self.source_path.exists():
            info["source_size"] = self.source_path.stat().st_size
        
        return info
    
    def save_embedded_readme(self, filename: str = "README.md") -> bool:
        """
        Save the embedded README to the target directory.
        
        Args:
            filename: Name for the saved README file (default: "README.md")
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        if not self.validate_target():
            return False
        
        target_file = self.target_path / filename
        
        try:
            target_file.write_text(get_embedded_readme(), encoding='utf-8')
            logger.info(f"Successfully saved embedded README to {target_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save embedded README: {e}")
            return False
    
    def save_full_readme(self, filename: str = "PYTHON_CHEATSHEET.md") -> bool:
        """
        Save the full embedded README (Python Cheatsheet) to the target directory.
        
        Args:
            filename: Name for the saved file (default: "PYTHON_CHEATSHEET.md")
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        if not self.validate_target():
            return False
        
        target_file = self.target_path / filename
        
        try:
            target_file.write_text(get_full_readme(), encoding='utf-8')
            logger.info(f"Successfully saved full README to {target_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save full README: {e}")
            return False


def copy_readme(
    source: Union[str, Path],
    target: Union[str, Path],
    overwrite: bool = False,
    rename: Optional[str] = None
) -> bool:
    """
    Convenience function to copy a README file.
    
    Args:
        source: Path to the source README file
        target: Path to the target directory
        overwrite: If True, overwrite existing file
        rename: Optional new name for the copied file
        
    Returns:
        bool: True if copy was successful, False otherwise
        
    Example:
        >>> copy_readme("README.md", "/path/to/project")
        >>> copy_readme("README.md", "/path/to/project", overwrite=True, rename="PROJECT_README.md")
    """
    copier = ReadmeCopier(source, target)
    return copier.copy(overwrite=overwrite, rename=rename)
