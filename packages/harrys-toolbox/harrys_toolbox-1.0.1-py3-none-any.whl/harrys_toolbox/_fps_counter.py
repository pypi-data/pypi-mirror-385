
import time

class FPSCounter:

    def __init__(self, refresh_rate=0.5):

        self._refresh_rate = refresh_rate

        self._fps = 0.0
        self._processing_time = 0.0
        self._processing_time_list = []

        self._last_call_time = 0.0
        self._update_time = 0.0

        self._simple_mode = False

    def tick(self, force=False):

        if self._simple_mode and (force == False):
            raise Exception(
                "FPS Error: Simple mode enabled by call to __str__"
                ", unable to use .tick()"
            )

        self._processing_time = time.time() - self._last_call_time
        self._last_call_time = time.time()

        self._processing_time_list.append(self._processing_time)

        if (time.time() - self._update_time) > self._refresh_rate:

            sum_of_processing_times = sum(self._processing_time_list)

            mean_processing_time = sum_of_processing_times / len(
                self._processing_time_list
            )

            self._fps = 1 / mean_processing_time
            self._processing_time_list = []
            self._update_time = time.time()

    def get_fps(self) -> float:
        return self._fps

    def get_processing_time(self) -> float:
        return self._processing_time

    def __str__(self) -> str:
        self._simple_mode = True

        self.tick(force=True)

        fps_count = round(self.get_fps(), 2)

        return f"FPS: {fps_count}"
