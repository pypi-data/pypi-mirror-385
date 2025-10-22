import configparser
from pathlib import Path
import aiofiles

class InoConfigHelper:
    def __init__(self, path='configs/base.ini', load_from: Path = None):
        self.debug = False
        self.path = Path(path)
        self.config = configparser.ConfigParser()
        if load_from is not None:
            self.config.read(load_from)

        self._load()

    def _load(self):
        self.config.read(self.path)

    def get(self, section, key, fallback=None):
        try:
            value = self.config.get(section, key, fallback=fallback)
            if isinstance(value, list):
                if self.debug:
                    print(f"❌ Config value for [{section}][{key}] is a list: {value}")
                return fallback
            if self.debug:
                print(f"🔎 Raw value for [{section}][{key}] = {value} ({type(value)})")
            if value is not None:
                value = value.strip()
            return value
        except Exception as e:
            print(f"❌ Failed to get str for [{section}][{key}]: {e}")
            return fallback

    def get_bool(self, section, key, fallback=False):
        try:
            value = self.config.getboolean(section, key, fallback=fallback)
            if self.debug:
                print(f"🔎 Raw value for [{section}][{key}] = {value} ({type(value)})")
            return value
        except Exception as e:
            print(f"❌ Failed to get boolean for [{section}][{key}]: {e}")
            return fallback

    def set(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}

        if self.debug:
            print(f"📝 Setting [{section}][{key}] = {value} ({type(value)})")

        self.config[section][key] = str(value).strip()

        self.save()

        self._load()

    async def set_async(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}

        if self.debug:
            print(f"📝 Setting [{section}][{key}] = {value} ({type(value)})")

        self.config[section][key] = str(value).strip()

        await self.save_async()

        self._load()

    def _is_valid_config(self):
        try:
            self.config.read(self.path)
            return bool(self.config.sections())
        except Exception:
            return False

    def save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w") as configfile:
                self.config.write(configfile)
        except Exception as e:
            print(f"❌ Failed to save config to {self.path}: {e}")
            raise

    async def save_async(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)

            from io import StringIO
            buffer = StringIO()
            self.config.write(buffer)
            content = buffer.getvalue()
            buffer.close()

            async with aiofiles.open(self.path, "w") as configfile:
                await configfile.write(content)
        except Exception as e:
            print(f"❌ Failed to save config asynchronously to {self.path}: {e}")
            raise