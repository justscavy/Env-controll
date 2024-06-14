from dataclasses import dataclass

@dataclass
class SharedState:
    light_state: int = 0
    humidifier_state: int = 0
    dehumidifier_state: int = 0
  
shared_state = SharedState()