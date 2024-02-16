from dynaconf import Dynaconf, Validator


def validate_settings(settings: Dynaconf) -> None:
    import os

    # settings.validators.register(
    #     Validator("MESSAGE_ENCRYPTION_KEY", must_exist=True, cast=str),
    # )
    settings.validators.validate_all()
