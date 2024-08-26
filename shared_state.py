from dataclasses import dataclass

@dataclass
class SharedState:
    min_vpd: float = 1.10  # Default min VPD value
    max_vpd: float = 1.20  # Default max VPD value
    light_state: int = 0
    humidifier_state: int = 0
    dehumidifier_state: int = 0
    heatmat_state: int = 0
    #fanexhaust2_state: int = 0 #TODO
shared_state = SharedState()

"""
@dataclass
class SharedState:
    min_vpd: float = 1.10  # Default min VPD value
    max_vpd: float = 1.20  # Default max VPD value
    light_state: bool = False
    humidifier_state: bool = False
    heatmat_state: bool = False
    dehumidifier_state: bool = False

shared_state = SharedState()
"""