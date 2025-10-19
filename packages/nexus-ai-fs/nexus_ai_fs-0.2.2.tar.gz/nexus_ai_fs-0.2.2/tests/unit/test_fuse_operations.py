"""Unit tests for FUSE operations.

These tests verify the FUSE filesystem mount functionality including
file operations, directory operations, and virtual file views.
"""

from __future__ import annotations

import errno
import os
import sys
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

# Mock the fuse module to allow tests to run without libfuse installed
sys.modules["fuse"] = MagicMock()


# Create mock FuseOSError class
class FuseOSError(OSError):
    """Mock FuseOSError for testing."""

    def __init__(self, errno: int):
        """Initialize with errno."""
        super().__init__(errno, os.strerror(errno))
        self.errno = errno


# Inject mock into fuse module
sys.modules["fuse"].FuseOSError = FuseOSError
sys.modules["fuse"].Operations = object
sys.modules["fuse"].FUSE = MagicMock

from nexus.fuse.mount import MountMode  # noqa: E402
from nexus.fuse.operations import NexusFUSEOperations  # noqa: E402

if TYPE_CHECKING:
    pass


@pytest.fixture
def mock_nexus_fs() -> MagicMock:
    """Create a mock Nexus filesystem."""
    fs = MagicMock(
        spec=["read", "write", "delete", "exists", "list", "is_directory", "mkdir", "rmdir"]
    )
    return fs


@pytest.fixture
def fuse_ops(mock_nexus_fs: MagicMock) -> NexusFUSEOperations:
    """Create FUSE operations with mock filesystem."""
    return NexusFUSEOperations(mock_nexus_fs, MountMode.SMART)


class TestVirtualPathParsing:
    """Test virtual path parsing logic."""

    def test_parse_regular_path(
        self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock
    ) -> None:
        """Test parsing regular path."""
        # Mock that the .txt file exists but the base doesn't (so it's a real .txt file)
        mock_nexus_fs.exists.return_value = False

        path, view = fuse_ops._parse_virtual_path("/workspace/file.txt")
        assert path == "/workspace/file.txt"
        assert view is None

    def test_parse_raw_path(self, fuse_ops: NexusFUSEOperations) -> None:
        """Test parsing .raw/ path."""
        path, view = fuse_ops._parse_virtual_path("/.raw/workspace/file.pdf")
        assert path == "/workspace/file.pdf"
        assert view is None

    def test_parse_txt_view(self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock) -> None:
        """Test parsing .txt virtual view."""
        # Mock base file exists
        mock_nexus_fs.exists.return_value = True

        path, view = fuse_ops._parse_virtual_path("/workspace/file.pdf.txt")
        assert path == "/workspace/file.pdf"
        assert view == "txt"

    def test_parse_md_view(self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock) -> None:
        """Test parsing .md virtual view."""
        # Mock base file exists
        mock_nexus_fs.exists.return_value = True

        path, view = fuse_ops._parse_virtual_path("/workspace/file.pdf.md")
        assert path == "/workspace/file.pdf"
        assert view == "md"


class TestGetattr:
    """Test getattr operation (get file attributes)."""

    def test_getattr_directory(
        self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock
    ) -> None:
        """Test getting attributes for a directory."""
        mock_nexus_fs.is_directory.return_value = True

        attrs = fuse_ops.getattr("/workspace")

        assert attrs["st_mode"] & 0o040000  # S_IFDIR
        assert attrs["st_nlink"] == 2

    def test_getattr_file(self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock) -> None:
        """Test getting attributes for a file."""
        mock_nexus_fs.is_directory.return_value = False
        mock_nexus_fs.exists.return_value = True
        mock_nexus_fs.read.return_value = b"Hello, World!"

        attrs = fuse_ops.getattr("/workspace/file.txt")

        assert attrs["st_mode"] & 0o100000  # S_IFREG
        assert attrs["st_size"] == 13
        assert attrs["st_nlink"] == 1

    def test_getattr_nonexistent(
        self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock
    ) -> None:
        """Test getting attributes for nonexistent file."""
        mock_nexus_fs.is_directory.return_value = False
        mock_nexus_fs.exists.return_value = False

        with pytest.raises(FuseOSError) as exc_info:
            fuse_ops.getattr("/nonexistent")

        assert exc_info.value.errno == errno.ENOENT

    def test_getattr_raw_directory(self, fuse_ops: NexusFUSEOperations) -> None:
        """Test getting attributes for .raw directory."""
        attrs = fuse_ops.getattr("/.raw")

        assert attrs["st_mode"] & 0o040000  # S_IFDIR
        assert attrs["st_nlink"] == 2


class TestReaddir:
    """Test readdir operation (list directory contents)."""

    def test_readdir_root(self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock) -> None:
        """Test listing root directory."""
        mock_nexus_fs.list.return_value = ["/workspace/", "/shared/"]

        entries = fuse_ops.readdir("/")

        assert "." in entries
        assert ".." in entries
        assert ".raw" in entries
        assert "workspace" in entries
        assert "shared" in entries

    def test_readdir_with_files(
        self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock
    ) -> None:
        """Test listing directory with files."""
        mock_nexus_fs.list.return_value = [
            "/workspace/file1.txt",
            "/workspace/file2.pdf",
        ]
        mock_nexus_fs.is_directory.return_value = False

        entries = fuse_ops.readdir("/workspace")

        assert "." in entries
        assert ".." in entries
        assert "file1.txt" in entries
        assert "file2.pdf" in entries
        # In smart mode, should also have virtual views
        assert "file2.pdf.txt" in entries
        assert "file2.pdf.md" in entries

    def test_readdir_binary_mode_no_virtual_views(self, mock_nexus_fs: MagicMock) -> None:
        """Test that binary mode doesn't add virtual views."""
        fuse_ops = NexusFUSEOperations(mock_nexus_fs, MountMode.BINARY)
        mock_nexus_fs.list.return_value = ["/workspace/file.pdf"]
        mock_nexus_fs.is_directory.return_value = False

        entries = fuse_ops.readdir("/workspace")

        assert "file.pdf" in entries
        assert "file.pdf.txt" not in entries
        assert "file.pdf.md" not in entries


class TestFileIO:
    """Test file I/O operations (open, read, write, release)."""

    def test_open_file(self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock) -> None:
        """Test opening a file."""
        # First check is in _parse_virtual_path (base file check - returns False)
        # Second check is for file existence (returns True)
        mock_nexus_fs.exists.side_effect = [False, True]

        fd = fuse_ops.open("/workspace/file.txt", os.O_RDONLY)

        assert fd > 0
        assert fd in fuse_ops.open_files
        assert fuse_ops.open_files[fd]["path"] == "/workspace/file.txt"

    def test_open_nonexistent(
        self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock
    ) -> None:
        """Test opening nonexistent file."""
        mock_nexus_fs.exists.return_value = False

        with pytest.raises(FuseOSError) as exc_info:
            fuse_ops.open("/nonexistent", os.O_RDONLY)

        assert exc_info.value.errno == errno.ENOENT

    def test_read_file(self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock) -> None:
        """Test reading file content."""
        mock_nexus_fs.exists.return_value = True
        mock_nexus_fs.read.return_value = b"Hello, World!"

        fd = fuse_ops.open("/workspace/file.txt", os.O_RDONLY)
        content = fuse_ops.read("/workspace/file.txt", 13, 0, fd)

        assert content == b"Hello, World!"

    def test_read_with_offset(
        self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock
    ) -> None:
        """Test reading file with offset."""
        mock_nexus_fs.exists.return_value = True
        mock_nexus_fs.read.return_value = b"Hello, World!"

        fd = fuse_ops.open("/workspace/file.txt", os.O_RDONLY)
        content = fuse_ops.read("/workspace/file.txt", 5, 7, fd)

        assert content == b"World"

    def test_write_new_file(self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock) -> None:
        """Test writing to a new file."""
        # create() needs exists to return False (not a virtual view)
        # write() needs exists to return False (file doesn't exist yet)
        mock_nexus_fs.exists.return_value = False

        fd = fuse_ops.create("/workspace/new.txt", 0o644)
        written = fuse_ops.write("/workspace/new.txt", b"Hello", 0, fd)

        assert written == 5
        mock_nexus_fs.write.assert_called()

    def test_write_virtual_view_fails(
        self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock
    ) -> None:
        """Test that writing to virtual views is not allowed."""
        # First call for exists check in open, second for virtual path check
        mock_nexus_fs.exists.side_effect = [True, True]

        fd = fuse_ops.open("/workspace/file.pdf.txt", os.O_RDONLY)

        with pytest.raises(FuseOSError) as exc_info:
            fuse_ops.write("/workspace/file.pdf.txt", b"data", 0, fd)

        assert exc_info.value.errno == errno.EROFS

    def test_release_file(self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock) -> None:
        """Test releasing (closing) a file."""
        mock_nexus_fs.exists.return_value = True

        fd = fuse_ops.open("/workspace/file.txt", os.O_RDONLY)
        fuse_ops.release("/workspace/file.txt", fd)

        assert fd not in fuse_ops.open_files


class TestFileCreationDeletion:
    """Test file and directory creation/deletion operations."""

    def test_create_file(self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock) -> None:
        """Test creating a new file."""
        # Mock that base path doesn't exist (not a virtual view)
        mock_nexus_fs.exists.return_value = False

        fd = fuse_ops.create("/workspace/new.txt", 0o644)

        assert fd > 0
        mock_nexus_fs.write.assert_called_with("/workspace/new.txt", b"")

    def test_create_virtual_view_fails(
        self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock
    ) -> None:
        """Test that creating virtual views is not allowed."""
        # Mock base file exists to trigger virtual view detection
        mock_nexus_fs.exists.return_value = True

        with pytest.raises(FuseOSError) as exc_info:
            fuse_ops.create("/workspace/file.pdf.txt", 0o644)

        assert exc_info.value.errno == errno.EROFS

    def test_unlink_file(self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock) -> None:
        """Test deleting a file."""
        # Mock that base path doesn't exist (not a virtual view)
        mock_nexus_fs.exists.return_value = False

        fuse_ops.unlink("/workspace/file.txt")

        mock_nexus_fs.delete.assert_called_with("/workspace/file.txt")

    def test_unlink_virtual_view_fails(
        self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock
    ) -> None:
        """Test that deleting virtual views is not allowed."""
        # Mock base file exists to trigger virtual view detection
        mock_nexus_fs.exists.return_value = True

        with pytest.raises(FuseOSError) as exc_info:
            fuse_ops.unlink("/workspace/file.pdf.txt")

        assert exc_info.value.errno == errno.EROFS

    def test_mkdir(self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock) -> None:
        """Test creating a directory."""
        fuse_ops.mkdir("/workspace/new_dir", 0o755)

        mock_nexus_fs.mkdir.assert_called_with("/workspace/new_dir", parents=True, exist_ok=True)

    def test_mkdir_in_raw_fails(
        self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock
    ) -> None:
        """Test that creating directories in .raw is not allowed."""
        with pytest.raises(FuseOSError) as exc_info:
            fuse_ops.mkdir("/.raw/workspace", 0o755)

        assert exc_info.value.errno == errno.EROFS

    def test_rmdir(self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock) -> None:
        """Test removing a directory."""
        fuse_ops.rmdir("/workspace/old_dir")

        mock_nexus_fs.rmdir.assert_called_with("/workspace/old_dir", recursive=False)

    def test_rmdir_raw_fails(self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock) -> None:
        """Test that removing .raw directory is not allowed."""
        with pytest.raises(FuseOSError) as exc_info:
            fuse_ops.rmdir("/.raw")

        assert exc_info.value.errno == errno.EROFS


class TestRename:
    """Test rename operation."""

    def test_rename_file(self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock) -> None:
        """Test renaming a file."""
        # Mock that neither path is a virtual view
        mock_nexus_fs.exists.return_value = False
        mock_nexus_fs.read.return_value = b"content"

        fuse_ops.rename("/workspace/old.txt", "/workspace/new.txt")

        mock_nexus_fs.read.assert_called_with("/workspace/old.txt")
        mock_nexus_fs.write.assert_called_with("/workspace/new.txt", b"content")
        mock_nexus_fs.delete.assert_called_with("/workspace/old.txt")

    def test_rename_virtual_view_fails(
        self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock
    ) -> None:
        """Test that renaming virtual views is not allowed."""
        # Mock base file exists for source to trigger virtual view detection
        mock_nexus_fs.exists.return_value = True

        with pytest.raises(FuseOSError) as exc_info:
            fuse_ops.rename("/workspace/file.pdf.txt", "/workspace/other.txt")

        assert exc_info.value.errno == errno.EROFS

    def test_rename_in_raw_fails(
        self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock
    ) -> None:
        """Test that renaming in .raw is not allowed."""
        with pytest.raises(FuseOSError) as exc_info:
            fuse_ops.rename("/.raw/file.txt", "/workspace/file.txt")

        assert exc_info.value.errno == errno.EROFS


class TestTruncate:
    """Test truncate operation."""

    def test_truncate_existing_file(
        self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock
    ) -> None:
        """Test truncating an existing file."""
        # First call for virtual path check (False), second for file exists (True)
        mock_nexus_fs.exists.side_effect = [False, True]
        mock_nexus_fs.read.return_value = b"Hello, World!"

        fuse_ops.truncate("/workspace/file.txt", 5)

        # Should write truncated content
        call_args = mock_nexus_fs.write.call_args
        assert call_args[0][0] == "/workspace/file.txt"
        assert call_args[0][1] == b"Hello"

    def test_truncate_expand(self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock) -> None:
        """Test truncating (expanding) a file."""
        # First call for virtual path check (False), second for file exists (True)
        mock_nexus_fs.exists.side_effect = [False, True]
        mock_nexus_fs.read.return_value = b"Hi"

        fuse_ops.truncate("/workspace/file.txt", 5)

        # Should pad with zeros
        call_args = mock_nexus_fs.write.call_args
        assert call_args[0][0] == "/workspace/file.txt"
        assert call_args[0][1] == b"Hi\x00\x00\x00"

    def test_truncate_virtual_view_fails(
        self, fuse_ops: NexusFUSEOperations, mock_nexus_fs: MagicMock
    ) -> None:
        """Test that truncating virtual views is not allowed."""
        # Mock base file exists to trigger virtual view detection
        mock_nexus_fs.exists.return_value = True

        with pytest.raises(FuseOSError) as exc_info:
            fuse_ops.truncate("/workspace/file.pdf.txt", 0)

        assert exc_info.value.errno == errno.EROFS


class TestMountModes:
    """Test different mount modes."""

    def test_binary_mode_returns_raw(self, mock_nexus_fs: MagicMock) -> None:
        """Test that binary mode returns raw content."""
        fuse_ops = NexusFUSEOperations(mock_nexus_fs, MountMode.BINARY)
        raw_content = b"\x89PNG\r\n\x1a\n"  # PNG header
        mock_nexus_fs.read.return_value = raw_content

        content = fuse_ops._get_file_content("/file.png", None)

        assert content == raw_content

    def test_text_mode_decodes_text(self, mock_nexus_fs: MagicMock) -> None:
        """Test that text mode decodes text files."""
        fuse_ops = NexusFUSEOperations(mock_nexus_fs, MountMode.TEXT)
        mock_nexus_fs.read.return_value = b"Hello, World!"

        content = fuse_ops._get_file_content("/file.txt", "txt")

        assert content == b"Hello, World!"

    def test_smart_mode_with_view(self, mock_nexus_fs: MagicMock) -> None:
        """Test that smart mode uses parser for virtual views."""
        fuse_ops = NexusFUSEOperations(mock_nexus_fs, MountMode.SMART)
        mock_nexus_fs.read.return_value = b"text content"

        # Should try to parse when view_type is specified
        content = fuse_ops._get_file_content("/file.txt", "txt")

        # Should return text (decoded UTF-8)
        assert content == b"text content"
