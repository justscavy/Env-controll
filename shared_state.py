import threading

class SharedState:
    def __init__(self):
        self._light_state = 0
        self._humidifier_state = 0  #
        self._lock = threading.Lock()

    @property
    def light_state(self):
        with self._lock:
            return self._light_state

    @light_state.setter
    def light_state(self, value):
        with self._lock:
            self._light_state = value

    @property
    def humidifier_state(self):
        with self._lock:
            return self._humidifier_state

    @humidifier_state.setter
    def humidifier_state(self, value):
        with self._lock:
            self._humidifier_state = value


shared_state = SharedState()
