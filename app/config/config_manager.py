import os
import json
import threading


class ConfigManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_path=None):
        if self._initialized:
            return
        self._initialized = True
        self._config_path = config_path or self._default_config_path()
        self._data = {}
        self._defaults = {}
        self._types = {}
        # 注册所有主要配置项
        self.register("SYMBOLS", ["USTECm", "XAUUSDm", "NAS100"], list)
        self.register("DEFAULT_TIMEFRAME", "M1", str)
        self.register("Delta_TIMEZONE", 0, int)
        self.register("TRADING_DAY_RESET_HOUR", 20, int)
        self.register("DAILY_LOSS_LIMIT", 150.0, float)
        self.register("DAILY_TRADE_LIMIT", 20, int)
        self.register(
            "GUI_SETTINGS",
            {
                "WINDOW_TOP": True,
                "SOUND_ALERT": True,
                "ALERT_SECONDS": 5,
                "BEEP_FREQUENCY": 1000,
                "BEEP_DURATION": 200,
                "BREAKEVEN_OFFSET_POINTS": 100,
            },
            dict,
        )
        self.register(
            "SL_MODE", {"DEFAULT_MODE": "CANDLE_KEY_LEVEL", "CANDLE_LOOKBACK": 3}, dict
        )
        self.register(
            "BREAKOUT_SETTINGS",
            {
                "HIGH_OFFSET_POINTS": 10,
                "LOW_OFFSET_POINTS": 10,
                "SL_OFFSET_POINTS": 100,
            },
            dict,
        )
        self.register(
            "BATCH_ORDER_DEFAULTS",
            {
                "order1": {
                    "volume": 0.01,
                    "sl_points": 3000,
                    "tp_points": 50000,
                    "sl_candle": 3,
                    "fixed_loss": 5.0,
                    "checked": True,
                },
                "order2": {
                    "volume": 0.01,
                    "sl_points": 3000,
                    "tp_points": 50000,
                    "sl_candle": 3,
                    "fixed_loss": 5.0,
                    "checked": True,
                },
                "order3": {
                    "volume": 0.01,
                    "sl_points": 3000,
                    "tp_points": 50000,
                    "sl_candle": 3,
                    "fixed_loss": 5.0,
                    "checked": True,
                },
                "order4": {
                    "volume": 0.21,
                    "sl_points": 3000,
                    "tp_points": 50000,
                    "sl_candle": 3,
                    "fixed_loss": 5.0,
                    "checked": False,
                },
            },
            dict,
        )
        self.register(
            "POSITION_SIZING",
            {"DEFAULT_MODE": "FIXED_LOSS", "DEFAULT_FIXED_LOSS": 15.0},
            dict,
        )
        self._load()

    def _default_config_path(self):
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        return os.path.join(project_root, "config", "config.json")

    def register(self, key, default, typ):
        self._defaults[key] = default
        self._types[key] = typ
        if key not in self._data:
            self._data[key] = default

    def get(self, key, default=None):
        return self._data.get(key, self._defaults.get(key, default))

    def set(self, key, value):
        if key in self._types:
            value = self._types[key](value)
        self._data[key] = value

    def load(self):
        self._load()

    def save(self):
        try:
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[ConfigManager] 保存配置失败: {e}")
            return False

    def _load(self):
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception as e:
                print(f"[ConfigManager] 加载配置失败: {e}")
                self._data = dict(self._defaults)
        else:
            self._data = dict(self._defaults)

    def all(self):
        return dict(self._data)


# 单例实例
config_manager = ConfigManager()
