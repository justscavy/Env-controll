import threading

class SharedState:
    def __init__(self):
        self._light_state = 0
        self._lock = threading.Lock()

    @property
    def light_state(self):
        with self._lock:
            return self._light_state

    @light_state.setter
    def light_state(self, value):
        with self._lock:
            self._light_state = value

# Create a single instance of SharedState to be imported wherever needed
shared_state = SharedState()
