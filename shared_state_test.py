from dataclasses import dataclass
'''
@dataclass
class SharedState:
    light_state: int = 0
    humidifier_state: int = 0
    dehumidifier_state: int = 0
    heatmat_state: int = 0
    #fanexhaust2_state: int = 0 #TODO
shared_state = SharedState()'''



@dataclass
class SharedState:
    min_vpd: float = 0.3        # Default minimum VPD value
    max_vpd: float = 3.0        # Default maximum VPD value
    min_temp: float = 18.0      # Default minimum temperature value
    max_temp: float = 32.0      # Default maximum temperature value
    light_state: bool = False
    humidifier_state: bool = False
    heatmat_state: bool = False
    dehumidifier_state: bool = False

shared_state = SharedState()


