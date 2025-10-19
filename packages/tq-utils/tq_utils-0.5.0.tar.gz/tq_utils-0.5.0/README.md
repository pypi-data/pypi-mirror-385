Util list:

- file_manager
   
  对 open() 的封装，添加了文件名有效性判断、路径缺失创建、读时文件缺失创建，等。
   
- singleton

  线程安全(加锁)单例模式的 metaclass.

- time_util

  时间相关工具，包括：timer, function timeout, ...

- tq_json
    
  对 Python 内置 json 模块，使用 FileManager 进行封装.

- tq_logger

  自己写的 logger

- tq_pickle

  对 Python 内置 pickle 模块，使用 FileManager 进行封装.

- tq_sqlite3

  对 Python 内置的 sqlite3 模块进行封装。

- tq_xml

  对 Python 内置的 xml.etree.ElementTree 模块进行封装。

- tq_yaml

  对第三方的 PyYAML 库，进行封装。