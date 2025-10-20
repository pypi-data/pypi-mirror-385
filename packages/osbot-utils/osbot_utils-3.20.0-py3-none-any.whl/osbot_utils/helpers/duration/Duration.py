from datetime                       import timedelta

from osbot_utils.helpers.duration.schemas.Schema__Duration import Schema__Duration
from osbot_utils.utils.Call_Stack   import Call_Stack
from osbot_utils.utils.Misc         import date_time_now, time_delta_to_str


class Duration:                                     # Helper class for to capture time duration
    def __init__(self, prefix="\nDuration:", print_result=True, use_utc=True, print_stack=False):
        self.use_utc            = use_utc
        self.print_result       = print_result
        self.prefix             = prefix
        self.start_time         = None
        self.end_time           = None
        self.duration           = None
        self.print_stack        = print_stack
        if True or print_stack:
            self.call_stack     = Call_Stack()

    def __enter__(self):
        if self.print_stack:
            self.call_stack.capture()
        self.start()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.end()

    def data(self) -> Schema__Duration: # Returns the duration data in Schema__Duration format.
        if not self.duration:
            raise ValueError("Duration has not been calculated yet. Call end() first.")

        return Schema__Duration( utc                = self.use_utc               ,
                                 timestamp_start    = self.start_time.timestamp(),
                                 timestamp_end      = self.end_time  .timestamp(),
                                 duration_seconds   = self.seconds             ())

    def start(self):
        self.start_time = date_time_now(use_utc=self.use_utc, return_str=False)

    def end(self):
        self.end_time = date_time_now(use_utc=self.use_utc, return_str=False)
        self.duration = self.end_time - self.start_time
        if self.print_result:
            print(f"{self.prefix} {time_delta_to_str(self.duration)}")
            if self.print_stack:
                self.call_stack.print()

    def milliseconds(self):
        return self.duration.total_seconds() * 1000

    def seconds(self):
        return self.duration.total_seconds()

    def set_duration(self,seconds:int):
        self.duration = timedelta(seconds=seconds)
        return self