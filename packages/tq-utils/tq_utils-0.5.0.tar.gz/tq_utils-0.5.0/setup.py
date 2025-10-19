from setuptools import setup, find_packages
import os.path

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = fh.read()

VERSION = '0.5.0'
DESCRIPTION = 'Some simple utils.'

setup(
    name='tq_utils',
    version=VERSION,
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    url='https://gitee.com/torchW/tqutils',
    author='TripleQuiz',
    author_email='triple_quiz@163.com',
    license='MIT',
    keywords=['python', 'util', 'file manager', 'singleton', 'timer', 'functon_timeout', 'json', 'logger', 'pickle',
              'sqlite3', 'xml', 'yaml'],
    python_requires='>=3.6, <3.12',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Intended Audience :: Developers',
        'Operating System :: Microsoft :: Windows',
        'Natural Language :: Chinese (Simplified)',
    ],
    packages=find_packages(include=['tq_utils', 'tq_utils.*']),
    install_requires=[  # 需要安装的第三方库及版本，e.g. 'pydot==3.0.1'
        'func-timeout>=4.3.5',
        'PyYAML>=6.0.3',
    ],
    include_package_data=True,
    exclude_package_data={},
    zip_safe=False,
)

"""
打包发布步骤：
1. 测试代码
2. commit & create tag（别忘了 setup 修改 version）
3. 打包源分发包和轮子，命令：python setup.py sdist bdist_wheel
4. PyPI发布，命令：twine upload -r tq_utils dist/*
"""
