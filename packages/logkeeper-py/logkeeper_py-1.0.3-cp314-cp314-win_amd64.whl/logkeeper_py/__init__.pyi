class LogKeeper:
    """
    Simple file logger that works out of the box with automatic timestamping and session management

    Example:
        >>> from logkeeper import LogKeeper
        >>> LogKeeper.info("Application started")
        >>> LogKeeper.save_logs()
    """

    @staticmethod
    def info(message: str) -> None:
        """Write an informational message to the log.

        Use this to record normal events that describe the general
        operation of your program — for example, initialization,
        task completion, or background operations.

        Args:
            message: The message text to write to the log.

        Example:
            >>> LogKeeper.info("User 'admin' successfully authenticated")
            >>> LogKeeper.info("Daily report generation completed")
        """
        ...

    @staticmethod
    def warning(message: str) -> None:
        """Write a warning message to the log.

        Use this when something unexpected happens that may cause
        issues later, but the program can still continue running.
        Warnings help you identify potential risks before they
        become real errors.

        Args:
            message: The warning message text.

        Example:
            >>> LogKeeper.warning("Disk space below 10% remaining")
            >>> LogKeeper.warning("Retrying API request after timeout")
        """
        ...

    @staticmethod
    def error(message: str) -> None:
        """Write an error message to the log.

        Use this for failures that prevent part of the application
        from working correctly, but which don’t require a full stop.
        Errors usually indicate recoverable problems or failed tasks.

        Args:
            message: The error message text.

        Example:
            >>> LogKeeper.error("Failed to connect to the database")
            >>> LogKeeper.error("Email delivery service returned 500")
        """
        ...

    @staticmethod
    def critical(message: str) -> None:
        """Write a critical message to the log.

        Use this for severe problems that require immediate attention
        or cause the application to shut down. These are unrecoverable
        conditions that often indicate corruption, data loss, or
        hardware-level failures.

        Args:
            message: The critical message text.

        Example:
            >>> LogKeeper.critical("Fatal configuration corruption detected")
            >>> LogKeeper.critical("Unrecoverable I/O failure during backup")
        """
        ...

    @staticmethod
    def save_logs() -> None:
        """Save and close the current log file.

        This method flushes any buffered log entries to disk and closes
        the file handle. Call it when your application is shutting down
        to make sure all messages are safely written.

        Example:
            >>> LogKeeper.info("Application shutting down")
            >>> LogKeeper.save_logs()
        """
        ...