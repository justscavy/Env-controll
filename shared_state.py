from dataclasses import dataclass

@dataclass
class SharedState:
    light_state: int = 0
    humidifier_state: int = 0
    dehumidifier_state: int = 0
    heatmat_state: int = 0
    #fanexhaust2_state: int = 0 #TODO
shared_state = SharedState()