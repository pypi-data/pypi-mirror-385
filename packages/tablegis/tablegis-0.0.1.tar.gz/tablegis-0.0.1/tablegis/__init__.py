import inspect
import pkgutil
from pathlib import Path

# 获取当前包的路径
pkg_path = Path(__file__).parent

# 自动发现并导出所有模块中的函数
__all__ = []
for _, module_name, _ in pkgutil.iter_modules([str(pkg_path)]):
    # 导入模块
    module = __import__(f"{__name__}.{module_name}", fromlist=["*"])
    # 遍历模块中的成员
    for name, obj in inspect.getmembers(module):
        # 只导出函数，并且不是私有函数（不以下划线开头）
        if inspect.isfunction(obj) and not name.startswith('_'):
            # 将函数添加到当前命名空间
            globals()[name] = obj
            # 将函数名添加到 __all__
            if name not in __all__:
                __all__.append(name)
