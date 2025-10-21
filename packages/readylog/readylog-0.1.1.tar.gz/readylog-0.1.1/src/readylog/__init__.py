from collections.abc import Callable
from logging import FileHandler, StreamHandler, _checkLevel, getLevelName
from pathlib import Path
from sys import modules


def create_dict_config(
    logfile: Path,
    app_name: str,
    console_log_level: str | int = "WARNING",
    file_log_level: str | int = "DEBUG",
    console_handler_factory: Callable = StreamHandler,
    file_handler_factory: Callable = FileHandler,
) -> dict[str, str]:
    console_log_level = _checkLevel(console_log_level)
    file_log_level = _checkLevel(file_log_level)
    min_level = getLevelName(min(console_log_level, file_log_level))

    custom_file_formatter_conf = {
        "format": "{message:<50s} {levelname:>9s} {asctime}.{msecs:03.0f} {module}({lineno}) {funcName}",
        "style": "{",
        "datefmt": "%a %H:%M:%S",
    }

    custom_console_formatter_conf = {
        "format": "{message:<50s} {levelname:>9s} {module}({lineno}) {funcName}",
        "style": "{",
        "datefmt": "%a %H:%M:%S",
    }

    root_file_formatter_conf = {
        "format": f"[ROOT LOG] {custom_file_formatter_conf['format']}",
        "style": "{",
        "datefmt": "%a %H:%M:%S",
    }

    root_console_formatter_conf = {
        "format": f"[ROOT LOG] {custom_console_formatter_conf['format']}",
        "style": "{",
        "datefmt": "%a %H:%M:%S",
    }

    formatters_dict = {
        "custom_file_formatter": custom_file_formatter_conf,
        "custom_console_formatter": custom_console_formatter_conf,
        "root_file_formatter": root_file_formatter_conf,
        "root_console_formatter": root_console_formatter_conf,
    }

    custom_console_handler_conf = {
        "()": console_handler_factory,
        "level": console_log_level,
        "formatter": "custom_console_formatter",
        "stream": "ext://sys.stderr",
    }

    custom_file_handler_conf = {
        "()": file_handler_factory,
        "level": file_log_level,
        "formatter": "custom_file_formatter",
        "filename": logfile,
        "mode": "w",
        "encoding": "utf-8",
    }

    root_console_handler_conf = {
        "()": console_handler_factory,
        "level": "DEBUG",
        "formatter": "root_console_formatter",
        "stream": "ext://sys.stderr",
    }

    root_file_handler_conf = {
        "()": file_handler_factory,
        "level": "DEBUG",
        "formatter": "root_file_formatter",
        "filename": logfile.with_stem(f"{logfile.stem}_root"),
        "mode": "w",
        "encoding": "utf-8",
    }

    handlers_dict = {
        "custom_console_handler": custom_console_handler_conf,
        "custom_file_handler": custom_file_handler_conf,
        "root_console_handler": root_console_handler_conf,
        "root_file_handler": root_file_handler_conf,
    }

    custom_logger_conf = {
        "propagate": False,
        "handlers": ["custom_file_handler", "custom_console_handler"],
        "level": min_level,
    }

    root_logger_conf = {
        "handlers": ["root_file_handler", "root_console_handler"],
        "level": "WARNING",
    }

    loggers_dict = {
        app_name: custom_logger_conf,
        "__main__": custom_logger_conf,
        f"{modules[__name__].__spec__.parent}.decorators": custom_logger_conf,
    }

    dict_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters_dict,
        "handlers": handlers_dict,
        "loggers": loggers_dict,
        "root": root_logger_conf,
        "incremental": False,
    }

    return dict_config
