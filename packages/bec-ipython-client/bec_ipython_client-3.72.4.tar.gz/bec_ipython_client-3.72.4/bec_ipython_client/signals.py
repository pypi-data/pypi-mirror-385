import signal
import threading
import time

from bec_lib.bec_errors import ScanInterruption

PAUSE_MSG = """
The Scan Queue is entering a paused state. These are your options for changing
the state of the queue:

%resume              Resume the scan.
%restart             Restart the scan.
%abort               Perform cleanup, then kill plan. Mark exit_stats='aborted'.
%halt                Emergency Stop: Do not perform cleanup --- just stop.
"""


class SignalHandler:
    """Context manager for signal handing

    If multiple signals come in quickly, they may not all be seen, quoting
    the libc manual:

      Remember that if there is a particular signal pending for your
      process, additional signals of that same type that arrive in the
      meantime might be discarded. For example, if a SIGINT signal is
      pending when another SIGINT signal arrives, your program will
      probably only see one of them when you unblock this signal.

    https://www.gnu.org/software/libc/manual/html_node/Checking-for-Pending-Signals.html
    """

    def __init__(self, sig, log=None):
        self.sig = sig
        self.interrupted = False
        self.count = 0
        self.log = log
        self.released = False
        self.original_handler = None

    def __enter__(self):
        self.interrupted = False
        self.count = 0

        self.original_handler = signal.getsignal(self.sig)

        def handler(signum, frame):
            self.interrupted = True
            self.count += 1
            if self.log is not None:
                self.log.debug("SignalHandler caught SIGINT; count is %r", self.count)
            if self.count > 10:
                orig_func = self.original_handler
                self.release()
                orig_func(signum, frame)

            self.handle_signals()

        signal.signal(self.sig, handler)
        return self

    def __exit__(self, _type, _value, _tb):
        self.release()

    def release(self):
        if self.released:
            return False
        signal.signal(self.sig, self.original_handler)
        self.released = True
        return True

    def handle_signals(self): ...


class SigintHandler(SignalHandler):
    def __init__(self, bec):
        super().__init__(signal.SIGINT)
        self.bec = bec
        self.last_sigint_time = None  # time most recent SIGINT was processed
        self.num_sigints_processed = 0  # count SIGINTs processed

    def handle_signals(self):
        current_scan = self.bec.queue.scan_storage.current_scan_info
        if not current_scan:
            raise KeyboardInterrupt

        status = current_scan.get("status").lower()
        if status not in ["running", "deferred_pause"]:
            raise KeyboardInterrupt

        if any(current_scan.get("is_scan")) and (
            self.last_sigint_time is None or time.time() - self.last_sigint_time > 10
        ):
            # reset the counter to 1
            # It's been 10 seconds since the last SIGINT. Reset.
            self.count = 1
            if self.last_sigint_time is not None:
                print("It has been 10 seconds since the last SIGINT. Resetting SIGINT handler.")

            threading.Thread(
                target=self.bec.queue.request_scan_interruption, args=(True,), daemon=True
            ).start()
            print(
                "A 'deferred pause' has been requested. The "
                "scan will pause at the next checkpoint. "
                "To pause immediately, hit Ctrl+C again in the "
                "next 10 seconds."
            )

            self.last_sigint_time = time.time()
            return

        # - Ctrl-C twice within 10 seconds or a direct command (e.g. mv) -> hard pause
        if self.bec._service_config.abort_on_ctrl_c:
            print("The scan will be aborted.")
            threading.Thread(target=self.bec.queue.request_scan_abortion, daemon=True).start()
            raise ScanInterruption("User abort.")
        print("A hard pause will be requested.")
        threading.Thread(
            target=self.bec.queue.request_scan_interruption, args=(False,), daemon=True
        ).start()
        raise ScanInterruption(PAUSE_MSG)
