# __init__.py

# 版本信息
try:
    # Python 3.8+：importlib.metadata
    from importlib.metadata import version, PackageNotFoundError
except Exception:
    # 兼容旧版 Python（如果你需要支持 <3.8，可以 pip install importlib-metadata）
    try:
        from importlib_metadata import version, PackageNotFoundError  # type: ignore
    except Exception:
        version = None
        PackageNotFoundError = Exception

if version is not None:
    try:
        __version__ = version("aifund")
    except PackageNotFoundError:
        # 包还没有被安装（例如直接用源码运行），回退到下面的方法
        __version__ = "0.0.0"
else:
    __version__ = "0.0.0"

from . import collect
from . import util
from .chart import stock_chart
from .collect import *
from .util import get_code_id, trans_num, lock_string, unlock_string
