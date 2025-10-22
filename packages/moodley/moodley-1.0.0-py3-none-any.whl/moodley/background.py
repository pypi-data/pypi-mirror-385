import sys
import subprocess
import os
import signal
import logging
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

APP_DIR = Path.home() / ".moodley"
APP_DIR.mkdir(exist_ok=True)
PID_FILE = APP_DIR / "worker.pid"


def run_worker(frequency: int, log_file: Path) -> None:
    """
    Main worker loop. This function runs in the background process.

    Args:
        frequency: Check interval in seconds
        log_file: Path to log file
    """
    from moodley.helpers import setup_logging
    from moodley.core import handle_fetch

    # Set up logging for background process
    setup_logging(is_background=True)
    logger.info(f"Worker started with check frequency: {frequency}s")

    try:
        while True:
            try:
                logger.info("Checking for new assignments...")
                handle_fetch()
                logger.info(f"Check complete. Next check in {frequency}s")
            except ValueError as e:
                # Configuration error - likely credentials not set
                logger.error(f"Configuration error: {e}")
                logger.info("Stopping worker due to configuration error")
                break
            except Exception as e:
                # Log but continue - temporary errors shouldn't kill the worker
                logger.error(f"Error during fetch: {e}")
                logger.info(f"Will retry in {frequency}s")

            time.sleep(frequency)

    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.exception(f"Worker crashed: {e}")
        sys.exit(1)


@dataclass
class ProcessConfig:
    """Configuration for background process."""
    frequency: int = 900  # seconds
    log_file: Path = APP_DIR / "moodley.log"

    def validate(self) -> None:
        """Ensure configuration is valid."""
        if self.frequency < 60:
            raise ValueError("Frequency must be at least 60 seconds")


class BackgroundWorker:
    """Manages background worker process lifecycle."""

    def __init__(self, config: Optional[ProcessConfig] = None):
        self.config = config or ProcessConfig()
        self.config.validate()

    def _get_stored_pid(self) -> Optional[int]:
        """Read PID from file, returns None if invalid."""
        if not PID_FILE.exists():
            return None

        try:
            return int(PID_FILE.read_text().strip())
        except (ValueError, IOError):
            logger.warning("Invalid PID file, removing...")
            PID_FILE.unlink(missing_ok=True)
            return None

    def _save_pid(self, pid: int) -> None:
        """Save PID to file."""
        try:
            PID_FILE.write_text(str(pid))
        except IOError as e:
            logger.error(f"Failed to save PID file: {e}")
            raise

    def _is_process_running(self, pid: int) -> bool:
        """Check if process with given PID is running."""
        try:
            if os.name == "nt":
                import ctypes
                handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)
                is_running = handle is not None
                if handle:
                    ctypes.windll.kernel32.CloseHandle(handle)
                return is_running
            else:
                os.kill(pid, 0)  # Signal 0: check if process exists
                return True
        except (OSError, ProcessLookupError):
            return False

    def start(self) -> int:
        """
        Start detached background worker.
        Returns the PID of the started process.
        """
        # Check if already running
        existing_pid = self._get_stored_pid()
        if existing_pid and self._is_process_running(existing_pid):
            logger.info(f"Worker already running (PID {existing_pid})")
            return existing_pid

        worker_cmd = [
            sys.executable,
            "-m", "moodley",
            "--run-worker",
            str(self.config.frequency),
        ]

        try:
            if os.name == "nt":
                proc = self._start_windows(worker_cmd)
            else:
                proc = self._start_unix(worker_cmd)

            self._save_pid(proc.pid)
            logger.info(
                f"Background worker started (PID {proc.pid}). "
                f"Logs: {self.config.log_file}"
            )
            return proc.pid

        except Exception as e:
            logger.error(f"Failed to start background worker: {e}")
            raise

    def _start_windows(self, cmd: list) -> subprocess.Popen:
        """Start detached process on Windows using STARTUPINFO."""
        import subprocess

        # Create startup info to hide the window
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE

        return subprocess.Popen(
            cmd,
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP,
            startupinfo=startupinfo,
            close_fds=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def _start_unix(self, cmd: list) -> subprocess.Popen:
        """Start detached process on Unix-like systems."""
        return subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setpgrp,
        )

    def stop(self) -> bool:
        """
        Stop the background worker.
        Returns True if process was stopped, False if already stopped.
        """
        pid = self._get_stored_pid()

        if pid is None:
            logger.info("No background worker found")
            return False

        if not self._is_process_running(pid):
            logger.info(f"Worker (PID {pid}) is not running")
            PID_FILE.unlink(missing_ok=True)
            return False

        try:
            if os.name == "nt":
                self._terminate_windows(pid)
            else:
                self._terminate_unix(pid)

            logger.info(f"Background worker (PID {pid}) stopped")
            return True

        except Exception as e:
            logger.error(f"Error stopping worker: {e}")
            return False
        finally:
            PID_FILE.unlink(missing_ok=True)

    def _terminate_unix(self, pid: int) -> None:
        """Terminate process on Unix-like systems."""
        os.kill(pid, signal.SIGTERM)

    def _terminate_windows(self, pid: int) -> None:
        """Terminate process on Windows."""
        import ctypes
        handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)
        if handle:
            ctypes.windll.kernel32.TerminateProcess(handle, -1)
            ctypes.windll.kernel32.CloseHandle(handle)

    def status(self) -> tuple[bool, Optional[int]]:
        """
        Check worker status.
        Returns (is_running, pid).
        """
        pid = self._get_stored_pid()
        if pid is None:
            return False, None

        is_running = self._is_process_running(pid)
        if not is_running:
            PID_FILE.unlink(missing_ok=True)

        return is_running, pid


def activate(frequency: int = 900) -> None:
    """Start background worker with given frequency (in seconds)."""
    config = ProcessConfig(frequency=frequency)
    worker = BackgroundWorker(config)
    worker.start()


def deactivate() -> None:
    """Stop background worker."""
    worker = BackgroundWorker()
    worker.stop()


def get_status() -> None:
    """Print background worker status."""
    worker = BackgroundWorker()
    is_running, pid = worker.status()

    if is_running:
        print(f"Background worker is running (PID {pid})")
    else:
        print("Background worker is not running")