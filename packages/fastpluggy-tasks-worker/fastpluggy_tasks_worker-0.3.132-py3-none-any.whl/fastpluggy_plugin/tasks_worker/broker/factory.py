# broker/factory.py


def get_broker():
    from ..config import TasksRunnerSettings
    setting = TasksRunnerSettings()

    if setting.BROKER_TYPE == "none":
        return None
    elif setting.BROKER_TYPE == "local":
        from .local import LocalBroker
        return LocalBroker()
    else:
        raise ValueError(f"Unsupported broker scheme: {setting.BROKER_TYPE}")
