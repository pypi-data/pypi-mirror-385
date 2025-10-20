import configparser
from pathlib import Path

class ConfigManager:
    def __init__(self, config_file: Path):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        if self.config_file.exists():
            self.config.read(self.config_file, encoding="utf-8")
        else:
            self._create_default_config()

    def _create_default_config(self):
        self.config["General"] = {
            "Mute": "False",
            "MuteInfo": "False",        # ← 新增
            "MuteWarning": "False",     # ← 新增
            "Theme": "light",
            "FontScale": "1"
        }
        self.config["FontSize"] = {
            "H1": "30",
            "H2": "24",
            "H3": "20",
            "H4": "18",
            "H5": "15",
            "H6": "12"
        }
        self.config["FontFamily"] = {
            "default": "futura_medium_bt.ttf",
            "bold": "Futura_Heavy_font.ttf",
            "black": "Futura_Extra_Black_font.ttf",
            "ocr": "OCR-A_Regular.ttf",
            "kl": "KleinCondensed-Medium.ttf",
            "zh": "HarmonyOS_Sans_TC_Regular.ttf",
            "zh_bold": "HarmonyOS_Sans_TC_Bold.ttf"
        }
        self.config["ColorsLight"] = {
            "bg": "#FFFFFF",
            "fg": "#000000",
            "bg2": "#D7F0FB",
            "fg2": "#10A0D0",
            "fg3": "#AD025B",
            "fg4": "#B59457",
            "fg5": "#933318",
            "fg6": "#007F00",
            "fg7": "#FFA500",
            "fg8": "#C0C1C0",
            "fg9": "#000000"
        }
        self.config["ColorsDark"] = {
            "bg": "#000000",
            "fg": "#FFFFFF",
            "bg2": "#003264",
            "fg2": "#10A0D0",
            "fg3": "#AD025B",
            "fg4": "#B59457",
            "fg5": "#933318",
            "fg6": "#007F00",
            "fg7": "#FFA500",
            "fg8": "#777777",
            "fg9": "#FFFFFF"
        }
        self.config["LineWidth"] = {
            "default": "2"
        }
        
        self.save()

    def get(self, section, key, cast=str):
        value = self.config.get(section, key, fallback=None)
        if value is None:
            return None
        if cast == bool:
            return value.lower() in ("true", "1", "yes")
        if cast == int:
            return int(value)
        if cast == float:
            return float(value)
        return value

    def set(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = str(value)

    def save(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            self.config.write(f)

# 用法
if __name__ == "__main__":
    CONFIG_PATH = Path(__file__).resolve().parent / "pymeili_resource" / "config.ini"
    config = ConfigManager(CONFIG_PATH)

    mute_status = config.get("General", "Mute", bool)
    theme = config.get("General", "Theme")
    color_bg = config.get("ColorsLight", "bg")
    print(f"Current settings: Mute={mute_status}, Theme={theme}", 
          f"Background Color={color_bg}")

    config.set("General", "Mute", True)
    config.save()
    
    config._create_default_config()  # 创建默认配置文件

