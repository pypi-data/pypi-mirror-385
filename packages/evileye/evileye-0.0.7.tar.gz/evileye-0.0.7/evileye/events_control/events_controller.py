from threading import Thread
from queue import Queue
from timeit import default_timer as timer
import time
import copy
from ..core.base_class import EvilEyeBase


class EventsDetectorsController(EvilEyeBase):
    def __init__(self, events_detectors: list):
        super().__init__()
        self.control_thread = Thread(target=self.run)
        self.queue_out = Queue()
        self.detectors = events_detectors
        self.run_flag = False

        self.params = None
        self.events_detectors = {}  # Словарь, содержащий события, распределенные по детекторам

        self.any_events = False

    def set_params_impl(self):
        pass

    def get_params_impl(self):
        return dict()

    def init_impl(self):
        self.events_detectors = {detector.get_name(): [] for detector in self.detectors}

    def is_running(self):
        return self.run_flag

    def get(self):
        if self.queue_out.empty():
            return {}
        else:
            return self.queue_out.get()

    def run(self):
        while self.run_flag:
            time.sleep(0.01)
            self.any_events = False  # Для отслеживания, были ли обнаружены события
            begin_it = timer()

            # Получаем от детекторов события
            for detector in self.detectors:
                events = detector.get()
                if events:
                    self.events_detectors[detector.get_name()] = events
                    self.any_events = True
                else:
                    self.events_detectors[detector.get_name()] = []

            if self.any_events:
                self.queue_out.put(copy.deepcopy(self.events_detectors))
            end_it = timer()

    def start(self):
        self.run_flag = True
        self.control_thread.start()

    def stop(self):
        # Try to flush one more batch of events before stopping
        try:
            self.flush_once()
        except Exception:
            pass
        self.run_flag = False
        # Join control thread to ensure pending processing completed
        try:
            if self.control_thread.is_alive():
                self.control_thread.join(timeout=0.3)
        except Exception:
            pass

    def flush_once(self):
        """Collect events from detectors once and push to queue if any."""
        try:
            self.any_events = False
            # небольшая задержка чтобы детекторы успели выложить события
            time.sleep(0.01)
            for detector in self.detectors:
                events = detector.get()
                if events:
                    self.events_detectors[detector.get_name()] = events
                    self.any_events = True
                else:
                    self.events_detectors[detector.get_name()] = []
            if self.any_events:
                self.queue_out.put(copy.deepcopy(self.events_detectors))
            return self.any_events
        except Exception:
            return False
        if self.control_thread.is_alive():
            self.control_thread.join()
        self.logger.info('Everything in controller stopped')

    def default(self):
        pass

    def reset_impl(self):
        pass

    def release_impl(self):
        self.stop()
        self.logger.info('Everything in controller released')
