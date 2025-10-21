from engrate_kit.core.conf import DefaultSettings


class AppSettings(DefaultSettings):
    DEBUG: bool = True


settings = AppSettings()
