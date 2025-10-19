"""
This module defines custom exceptions for cryptographic operations.
"""


class CryptoError(Exception):
    """
    An exception that indicates an error occurred during a cryptographic operation.

    This exception is raised when encryption, decryption, or other related operations
    fail due to invalid input, configuration issues, or unexpected errors.

    Inherits:
        Exception: The base class for all built-in exceptions.

    Attributes:
        message (str): A descriptive message about the cause of the error.
    """

    def __init__(self, message="Error while attempting to perform a crypto operation."):
        """
        Initializes the CryptoError exception with an optional error message.

        Args:
            message (str, optional): Error message describing the problem. Default is
            "Error while attempting to perform a crypto operation."
        """
        super().__init__(message)
