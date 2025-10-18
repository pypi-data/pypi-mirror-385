"""Tests for the copier module."""
import pytest
import tempfile
import shutil
from pathlib import Path
from readme_copier.copier import ReadmeCopier, copy_readme


@pytest.fixture
def temp_dirs():
    """Create temporary source and target directories."""
    source_dir = tempfile.mkdtemp()
    target_dir = tempfile.mkdtemp()
    
    # Create a sample README file
    readme_path = Path(source_dir) / "README.md"
    readme_path.write_text("# Sample README\n\nThis is a test README file.")
    
    yield readme_path, Path(target_dir)
    
    # Cleanup
    shutil.rmtree(source_dir)
    shutil.rmtree(target_dir)


def test_readme_copier_init(temp_dirs):
    """Test ReadmeCopier initialization."""
    source_path, target_path = temp_dirs
    copier = ReadmeCopier(source_path, target_path)
    
    assert copier.source_path == source_path
    assert copier.target_path == target_path


def test_validate_source(temp_dirs):
    """Test source validation."""
    source_path, target_path = temp_dirs
    copier = ReadmeCopier(source_path, target_path)
    
    assert copier.validate_source() is True
    
    # Test with non-existent source
    copier_invalid = ReadmeCopier("nonexistent.md", target_path)
    assert copier_invalid.validate_source() is False


def test_validate_target(temp_dirs):
    """Test target validation."""
    source_path, target_path = temp_dirs
    copier = ReadmeCopier(source_path, target_path)
    
    assert copier.validate_target() is True
    
    # Test with new directory that needs to be created
    new_target = target_path / "new_subdir"
    copier_new = ReadmeCopier(source_path, new_target)
    assert copier_new.validate_target() is True
    assert new_target.exists()


def test_copy_success(temp_dirs):
    """Test successful file copy."""
    source_path, target_path = temp_dirs
    copier = ReadmeCopier(source_path, target_path)
    
    result = copier.copy()
    assert result is True
    
    copied_file = target_path / "README.md"
    assert copied_file.exists()
    assert copied_file.read_text() == source_path.read_text()


def test_copy_with_rename(temp_dirs):
    """Test copying with rename."""
    source_path, target_path = temp_dirs
    copier = ReadmeCopier(source_path, target_path)
    
    result = copier.copy(rename="NEW_README.md")
    assert result is True
    
    copied_file = target_path / "NEW_README.md"
    assert copied_file.exists()


def test_copy_without_overwrite(temp_dirs):
    """Test that copy fails without overwrite flag."""
    source_path, target_path = temp_dirs
    copier = ReadmeCopier(source_path, target_path)
    
    # First copy
    copier.copy()
    
    # Second copy without overwrite should fail
    result = copier.copy(overwrite=False)
    assert result is False


def test_copy_with_overwrite(temp_dirs):
    """Test that copy succeeds with overwrite flag."""
    source_path, target_path = temp_dirs
    copier = ReadmeCopier(source_path, target_path)
    
    # First copy
    copier.copy()
    
    # Modify source
    source_path.write_text("# Updated README\n\nThis is updated content.")
    
    # Second copy with overwrite should succeed
    result = copier.copy(overwrite=True)
    assert result is True
    
    copied_file = target_path / "README.md"
    assert "Updated README" in copied_file.read_text()


def test_get_info(temp_dirs):
    """Test get_info method."""
    source_path, target_path = temp_dirs
    copier = ReadmeCopier(source_path, target_path)
    
    info = copier.get_info()
    
    assert "source_path" in info
    assert "source_exists" in info
    assert "target_path" in info
    assert "target_exists" in info
    assert info["source_exists"] is True
    assert info["target_exists"] is True
    assert "source_size" in info


def test_copy_readme_function(temp_dirs):
    """Test the convenience copy_readme function."""
    source_path, target_path = temp_dirs
    
    result = copy_readme(source_path, target_path)
    assert result is True
    
    copied_file = target_path / "README.md"
    assert copied_file.exists()
