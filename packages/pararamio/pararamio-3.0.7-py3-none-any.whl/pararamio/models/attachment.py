"""Sync Attachment model."""

from __future__ import annotations

from dataclasses import dataclass
from io import BufferedReader, BytesIO
from os import PathLike
from typing import BinaryIO

from pararamio._core.models.attachment import CoreAttachment

__all__ = ('Attachment',)


@dataclass
class Attachment:
    """File attachment representation.

    This is a utility class for handling file attachments before upload.
    It can handle various file input types and provides helpers for
    filename and content type detection.
    """

    file: str | bytes | PathLike[str] | BytesIO | BinaryIO
    filename: str | None = None
    content_type: str | None = None

    @property
    def guess_filename(self) -> str:
        """Guess filename from the file object.

        Returns:
            Guessed filename or 'unknown'
        """
        return CoreAttachment.guess_filename_from_file(self.file, self.filename)

    @property
    def guess_content_type(self) -> str:
        """Guess content type from file.

        Returns:
            MIME type string
        """
        return CoreAttachment.guess_content_type_from_file(self.file, self.content_type)

    @property
    def fp(self) -> BytesIO | BinaryIO:
        """Get file pointer.

        Returns:
            File-like object

        Raises:
            TypeError: If a file type is not supported
        """
        return CoreAttachment.get_file_pointer(self.file)

    def __str__(self) -> str:
        """String representation."""
        return f'Attachment({self.guess_filename})'

    @staticmethod
    def get_file_pointer(
        file: str | bytes | PathLike[str] | BytesIO | BinaryIO,
    ) -> BytesIO | BinaryIO:
        """Get file pointer from various file types."""
        return CoreAttachment.get_file_pointer(file)

    @staticmethod
    def guess_content_type_from_file(
        file: str | bytes | PathLike[str] | BytesIO | BinaryIO | BufferedReader,
        content_type: str | None = None,
    ) -> str:
        """Guess content type from a file object."""
        return CoreAttachment.guess_content_type_from_file(file, content_type)

    @staticmethod
    def guess_filename_from_file(
        file: str | bytes | PathLike[str] | BytesIO | BinaryIO, filename: str | None = None
    ) -> str:
        """Guess filename from a file object."""
        return CoreAttachment.guess_filename_from_file(file, filename)
