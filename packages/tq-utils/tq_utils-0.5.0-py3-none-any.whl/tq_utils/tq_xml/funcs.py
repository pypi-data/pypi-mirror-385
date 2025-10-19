from typing import Union, Optional, Dict, Any
from datetime import date

from tq_utils.file_manager import FileManager

import xml.etree.ElementTree as ET
from xml.dom import minidom


def _xml_to_dict(element: ET.Element, child_key_mapping: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    通用递归将 XML 元素树转换为字典

    :param element: XML 元素
    :param child_key_mapping: 子标签名到字典键名的映射，如 {'Event': 'events'}
    :return: 标准化的字典结构
    {
        'tag': '标签名称',
        'attributes': {'属性名': '属性值', ...},
        '子标签列表1': [
            {
                'tag': '子标签名称',
                'attributes': {...},
                '子子标签列表': [...],
                ...
            },
            ...
        ],
        '子标签列表2': [...],
        ...
    }
    """
    # 基础结构
    result_dict = {
        "tag": element.tag,
        "attributes": element.attrib.copy() if element.attrib else {}
    }

    # 处理所有子元素
    children = list(element)
    if children:
        child_dict = {}

        for child in children:
            child_tag = child.tag

            # 递归处理子元素
            child_data = _xml_to_dict(child, child_key_mapping)

            # 确定存储的键名（使用映射或默认规则）
            if child_key_mapping and child_tag in child_key_mapping:
                storage_key = child_key_mapping[child_tag]
            else:
                # 默认规则：标签名转为复数形式
                storage_key = f"{child_tag.lower()}s"

            # 添加到子字典
            if storage_key not in child_dict:
                child_dict[storage_key] = []
            child_dict[storage_key].append(child_data)

        # 将子字典合并到结果中
        result_dict.update(child_dict)

    return result_dict


def loads_safe(xml_string: Union[str, bytes], child_key_mapping: Optional[Dict[str, str]] = None,
               return_element=False) -> Union[ET.Element, dict]:
    """
    解析 XML 文本内容
    :param xml_string: xml 文件内容
    :param child_key_mapping: 子标签名到字典键名的映射，如 {'Event': 'events'}
    :param return_element: 是否直接返回 root(ET.Element)，自己进行解析；默认为 False，将全部内容转换为 Python 内置基础结构
    :return: 标准化的字典结构
    {
        'tag': '标签名称',
        'attributes': {'属性名': '属性值', ...},
        '子标签列表1': [
            {
                'tag': '子标签名称',
                'attributes': {...},
                '子子标签列表': [...],
                ...
            },
            ...
        ],
        '子标签列表2': [...],
        ...
    }
    """
    try:
        root = ET.fromstring(xml_string)
        if return_element:
            return root
        return _xml_to_dict(root, child_key_mapping)
    except ET.ParseError as e:
        raise RuntimeError('XML 解析错误', e)


def load_safe(xml_file: str, child_key_mapping: Optional[Dict[str, str]] = None,
              return_element=False) -> Union[ET.Element, dict]:
    """
    解析 XML 文件内容
    :param xml_file: XML 文件
    :param child_key_mapping: 子标签名到字典键名的映射，如 {'Event': 'events'}
    :param return_element: 是否直接返回 root(ET.Element)，自己进行解析；默认为 False，将全部内容转换为 Python 内置基础结构
    :return: 标准化的字典结构
    {
        'tag': '标签名称',
        'attributes': {'属性名': '属性值', ...},
        '子标签列表1': [
            {
                'tag': '子标签名称',
                'attributes': {...},
                '子子标签列表': [...],
                ...
            },
            ...
        ],
        '子标签列表2': [...],
        ...
    }
    """
    with FileManager(xml_file, 'r', encoding='utf8') as f:
        xml_string = f.read()
        return loads_safe(xml_string, child_key_mapping, return_element)


def create_root_element(tag: str, time_atr=True, **attributes) -> ET.Element:
    """
    创建根元素
    :param tag: Tag name
    :param time_atr: 是否添加 date 属性
    :param attributes: 后续的参数将作为标签的属性
    :return: 创建的元素对象，like '<Tag id="1" type="error">Some text</Tag>'
    """
    if time_atr:
        attributes.setdefault('date', date.today().strftime('%Y-%m-%d'))
    # attrib 和 extra 都是标签属性设置的方式，一个是通过字典传入，一个通过关键字的方式
    return ET.Element(tag, attrib=attributes)


def create_sub_element(parent: ET.Element, tag: str, text: Optional[str] = "", **attributes) -> ET.Element:
    """
    添加带属性的标签
    :param parent: parent element
    :param tag: Tag name
    :param text: 标签文本内容。若为 None，则标签为自闭和标签 '<Tag/>'
    :param attributes: 后续的参数将作为标签的属性
    :return: 创建的元素对象，like '<Tag id="1" type="error">Some text</Tag>'
    """
    elem = ET.SubElement(parent, tag, attrib=attributes)
    if text is not None:
        elem.text = text
    return elem


def dumps_safe(root: ET.Element, indent=2) -> str:
    """
    转存数据到 XML 文本
    :param root: 数据
    :param indent: XML 格式缩进长度
    :return str: 转换的 XML 内容
    """
    # 转换为字符串（未格式化）
    rough_string = ET.tostring(root, encoding='utf-8')
    # 使用 minidom 美化
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent=" " * indent, encoding='utf-8')

    return pretty_xml.decode('utf-8')


def dump_safe(root: ET.Element, output_file: str, indent=2):
    """
    转存数据到 XML 文件
    :param root: 数据
    :param output_file: 输出文件
    :param indent: XML 格式缩进长度
    """
    # 无法优化格式，无换行和缩进
    # tree = ET.ElementTree(root)
    # # 写入文件
    # tree.write(output_file, encoding='utf-8', xml_declaration=True)

    pretty_xml_str = dumps_safe(root, indent)
    with FileManager(output_file, 'w', encoding='utf-8') as f:
        f.write(pretty_xml_str)
