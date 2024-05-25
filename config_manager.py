import json

class ConfigManager:
    def __init__(self, config_file="config/config.json"):
        self.config = self._read_config(config_file)
        self.influxdb_config = self.config.get("influxdb", {})
        self.email_config = self.config.get("email", {})
        
    def _read_config(self, file_path):
        with open(file_path) as f:
            return json.load(f)

    @property
    def influxdb_url(self):
        return self.influxdb_config.get("url")

    @property
    def influxdb_token(self):
        return self.influxdb_config.get("token")

    @property
    def influxdb_org(self):
        return self.influxdb_config.get("org")

    @property
    def influxdb_bucket(self):
        return self.influxdb_config.get("bucket")

    @property
    def email_to(self):
        return self.email_config.get("to_email")

    @property
    def email_from(self):
        return self.email_config.get("from_email")

    @property
    def email_password(self):
        return self.email_config.get("email_password")
