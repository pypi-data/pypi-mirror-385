# Native
import logging
import inspect
import os
from datetime import datetime


def get_module_name():
    frame = inspect.currentframe()
    if frame and frame.f_back and frame.f_back.f_back:
        caller_frame = frame.f_back.f_back
        caller_module = inspect.getmodule(caller_frame)
        if caller_module and caller_module.__name__ != __name__:
            module_parts = caller_module.__name__.split('.')
            return module_parts[-1] if module_parts else ''
    return os.path.splitext(os.path.basename(__file__))[0]


class FunctionNameLogger(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        frame = inspect.currentframe().f_back.f_back
        function_name = frame.f_code.co_name
        if function_name == '<module>':
            return msg, kwargs
        return f"[{function_name}] {msg}", kwargs


def get_logger():
    module_name = get_module_name()
    base_logger = logging.getLogger(f"{module_name}.{__name__}")
    base_logger.setLevel(logging.DEBUG)

    if not base_logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        base_logger.addHandler(handler)

    return FunctionNameLogger(base_logger, {})


logger = get_logger()
processing_date = datetime.now().strftime("%Y-%m-%d")