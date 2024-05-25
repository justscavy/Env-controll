import json
from dataclasses import dataclass



@dataclass
class InfluxDBConfig:
    url: str = ""
    token: str = ""
    org: str = ""
    bucket: str = ""

@dataclass
class EmailConfig:
    to_email: str = ""
    from_email: str = ""
    email_password: str = ""

class ConfigManager:
    def __init__(self, config_file="config/config.json"):
        self.config = self._read_config(config_file)
        self.influxdb_config = InfluxDBConfig(**self.config.get("influxdb", {}))
        self.email_config = EmailConfig(**self.config.get("email", {}))

    def _read_config(self, file_path):
        with open(file_path) as f:
            return json.load(f)

