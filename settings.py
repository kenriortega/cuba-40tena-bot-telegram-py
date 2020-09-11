import yaml
from dataclasses import dataclass
import os
redis_config = {
    "host": os.getenv('REDIS_URI'),
    "port": os.getenv('REDIS_PORT'),
    "password": os.getenv('REDIS_PASS'),
    "db": 0,
}


@dataclass
class SettingFile():
    file_path: str

    def load_external_services_file(self) -> dict:
        with open(self.file_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
