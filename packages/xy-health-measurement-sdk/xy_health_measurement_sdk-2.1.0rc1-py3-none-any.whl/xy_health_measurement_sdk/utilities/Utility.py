from base64 import b64encode
from copy import deepcopy
from importlib.resources import path as resources_path
from json import load
from multiprocessing import Value, Array
from re import sub
from ..protos.Validation_pb2 import Validation, UnknownError


class Utility(object):
    with resources_path('xy_health_measurement_sdk.resources', 'config.json') as config:
        with open(config, 'r', encoding='utf-8') as file:
            __config = load(file)
            __validation = __config['validation']

    @classmethod
    def get_validation(cls, code: Validation):
        # validation子节点配置会在业务中根据情况修改作为返回值
        # 深度拷贝可以防止业务修改影响全局默认配置
        return deepcopy(cls.__validation.get(Validation.Name(code)))

    @classmethod
    def get_config(cls, key):
        return cls.__config[key]

    @classmethod
    def assure_adequate_frames(cls, duration, frames_cnt, measurement_duration=None):
        min_measurement_duration = cls.get_config('min_measurement_duration')

        measurement_duration = measurement_duration if measurement_duration and measurement_duration >= min_measurement_duration else min_measurement_duration
        return duration >= measurement_duration and frames_cnt >= cls.get_config(
            'min_frames_cnt') * measurement_duration / min_measurement_duration

    @staticmethod
    def get_shared_value(shared_value: Value):
        with shared_value.get_lock():
            return shared_value.value

    @staticmethod
    def set_shared_value(shared_value: Value, value):
        with shared_value.get_lock():
            shared_value.value = value

    @staticmethod
    def get_shared_char_array(shared_char_array: Array):
        return shared_char_array[:].decode().strip()

    @staticmethod
    def set_shared_char_array(shared_char_array: Array, value: str):
        length = len(shared_char_array)
        if len(value) > length:
            shared_char_array[:length] = value[:length].encode()
        else:
            shared_char_array[:len(value)] = value.encode()

    @staticmethod
    def serialize_message(message):
        return b64encode(message.SerializeToString()).decode('utf-8')

    @staticmethod
    def generate_error(code=None, raising=True, **kwargs):
        """
        kwargs:{
            config: {
                'code': 3016,
                'level': 1,
                'msg': 1
            },
            message: '',
            exception: ex
        }
        obj:
        {
            'config': {
                'code': 3016,
                'level': 1,
                'msg': 1
            },
            'addition': {
                'message': f'failed to authenticate app_id:{app_id} sdk_key:{sdk_key} {exception}',
                'exception': exception
            }
        }
        """
        obj = {'config': kwargs.get('config', {})}
        code = code if code is not None else kwargs['config']['code']
        obj['config']['code'] = code

        addition = {}
        message, exception = kwargs.get('message'), kwargs.get('exception')
        if message:
            addition['message'] = message
        if exception:
            addition['exception'] = exception
        if addition:
            obj['addition'] = addition

        error = ValueError(obj)
        if raising:
            raise error
        return error

    @classmethod
    def validate_error(cls, error: Exception):
        """
        验证是否为中断性错误
        """
        kwargs = error.args[0] if isinstance(error, ValueError) else {'config': {'code': UnknownError}}
        exception_config = cls.__get_validation_args(**kwargs['config'])
        return exception_config['level'] == 'error', exception_config, kwargs.get('addition', {})

    @classmethod
    def __get_validation_args(cls, **kwargs):
        code = kwargs['code']
        exception = cls.get_validation(code)['exception']
        kwargs['msg_cn'] = kwargs.get('msg_cn', kwargs.get('msg', 0))

        for key in exception:
            exception[key] = sub(r'\[(.+?),(.+?)\]', lambda mc: mc.group(kwargs.get(key, 0) + 1), exception[key])
        exception['code'] = code
        return exception
