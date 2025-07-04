import yaml
import os
from pathlib import Path

class Config:
    def __init__(self):
        self.config_path = Path(__file__).parent.parent.parent / "config.yaml"
        self.load_config()
    
    def load_config(self):
        with open(self.config_path, 'r') as file:
            self.config = yaml.safe_load(file)
    
    def get(self, key, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, {})
        return value or default
    
    @property
    def openai_api_key(self):
        return os.getenv('OPENAI_API_KEY')
    
    @property
    def browser_config(self):
        return self.config.get('browser', {})
