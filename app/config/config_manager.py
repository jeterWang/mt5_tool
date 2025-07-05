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
        self.register("SL_MODE", "FIXED_POINTS", str)
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
            {"DEFAULT_MODE": "FIXED_LOSS"},
            dict,
        )
        self.register("CANDLE_LOOKBACK", 3, int)
        self.register(
            "STATISTICS_SETTINGS",
            {
                "start_date": "2000-01-01",
                "end_date": "2025-12-31",
                "account": "",
                "symbol": "",
                "day_target": 0.3,
                "week_target": 0.5,
                "month_target": 0.6,
            },
            dict,
        )
        self._load()

    def _default_config_path(self):
        import sys

        # 如果是打包后的exe，使用exe同级目录
        if getattr(sys, 'frozen', False):
            # 打包后的exe环境
            exe_dir = os.path.dirname(sys.executable)
            config_path = os.path.join(exe_dir, "config", "config.json")
            print(f"[ConfigManager] 打包环境，配置路径: {config_path}")
            return config_path
        else:
            # 开发环境
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            config_path = os.path.join(project_root, "config", "config.json")
            print(f"[ConfigManager] 开发环境，配置路径: {config_path}")
            return config_path

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
            print(f"[ConfigManager] 正在保存配置到: {self._config_path}")
            print(f"[ConfigManager] 配置数据: {self._data}")

            # 确保目录存在
            config_dir = os.path.dirname(self._config_path)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
                print(f"[ConfigManager] 创建配置目录: {config_dir}")

            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4, ensure_ascii=False)

            print(f"[ConfigManager] 配置保存成功")
            return True
        except Exception as e:
            print(f"[ConfigManager] 保存配置失败: {e}")
            import traceback
            traceback.print_exc()
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

    def get_statistics_settings(self):
        return self.get("STATISTICS_SETTINGS")

    def set_statistics_settings(self, settings: dict):
        self.set("STATISTICS_SETTINGS", settings)
        self.save()


# 单例实例
config_manager = ConfigManager()
