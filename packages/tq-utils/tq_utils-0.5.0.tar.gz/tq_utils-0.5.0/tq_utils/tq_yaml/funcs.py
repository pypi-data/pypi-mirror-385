from typing import Union

from tq_utils.file_manager import FileManager
import yaml


def loads_safe(yaml_string: Union[str, bytes]) -> Union[dict, list]:
    """
    解析 YAML 文本内容（SafeLoader，支持基本数据类型，不支持 Python 对象序列化）
    :param yaml_string: yaml 文件内容
    """
    return yaml.load(yaml_string, Loader=yaml.SafeLoader)


def load_safe(yaml_file: str) -> Union[dict, list]:
    """
    解析 YAML 文件内容（SafeLoader，支持基本数据类型，不支持 Python 对象序列化）
    :param yaml_file: yaml 文件
    """
    with FileManager(yaml_file, 'r', encoding='utf-8') as f:
        return yaml.load(f, Loader=yaml.SafeLoader)


def dumps_safe(data, indent=2) -> str:
    """
    转存数据到 YAML 文本（SafeDumper，支持基本数据类型，不支持 Python 对象序列化）
    :param data: 数据
    :param indent: YAML 格式缩进长度
    :return str: 转换的 YAML 内容
    """
    return yaml.dump(data, Dumper=yaml.SafeDumper, allow_unicode=True, sort_keys=False, indent=indent)


def dump_safe(data, output_file: str, indent=2):
    """
    转存数据到 YAML 文件（SafeDumper，支持基本数据类型，不支持 Python 对象序列化）
    :param data: 数据
    :param output_file: 输出文件
    :param indent: YAML 格式缩进长度
    """
    with FileManager(output_file, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, yaml.SafeDumper, allow_unicode=True, sort_keys=False, indent=indent)
