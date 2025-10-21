import struct
import ctypes
from ctypes import *
import os
import sys
import platform

# 判断你的python环境是64位还是32位
__RuntimeEnvironment = struct.calcsize("P") * 8 == 64

# 获取当前模块所在目录
__module_dir = os.path.dirname(os.path.abspath(__file__))


def _get_library_path():
    """
    根据操作系统和架构获取库文件路径
    支持 Windows (.dll)、Linux (.so)、macOS (.dylib)
    """
    system = platform.system().lower()
    is_64bit = __RuntimeEnvironment

    # 定义库文件名
    if system == "windows":
        lib_name = "SunnyNet64.dll" if is_64bit else "SunnyNet.dll"
    elif system == "linux":
        lib_name = "SunnyNet64.so" if is_64bit else "SunnyNet.so"
    elif system == "darwin":  # macOS
        lib_name = "SunnyNet64.dylib" if is_64bit else "SunnyNet.dylib"
    else:
        raise OSError(f"不支持的操作系统: {system}")

    # 尝试多个可能的路径
    possible_paths = [
        os.path.join(__module_dir, lib_name),  # 包目录下
        os.path.join(os.getcwd(), lib_name),  # 当前工作目录
        os.path.join(os.getcwd(), "SunnyNet", lib_name),  # 当前目录下的SunnyNet子目录
        lib_name,  # 系统库路径
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    # 如果都找不到，返回第一个路径（会在加载时报错）
    return possible_paths[0]


try:
    # 获取库文件路径
    lib_path = _get_library_path()

    # 加载共享库
    lib = CDLL(lib_path)

    if __RuntimeEnvironment:
        # 64位环境 - Go语言回调函数声明
        TcpCallback = CFUNCTYPE(
            None,
            c_int64,
            c_char_p,
            c_char_p,
            c_int64,
            c_int64,
            c_int64,
            c_int64,
            c_int64,
            c_int64,
        )
        HttpCallback = CFUNCTYPE(
            None,
            c_int64,
            c_int64,
            c_int64,
            c_int64,
            c_char_p,
            c_char_p,
            c_char_p,
            c_int64,
        )
        WsCallback = CFUNCTYPE(
            None,
            c_int64,
            c_int64,
            c_int64,
            c_int64,
            c_char_p,
            c_char_p,
            c_int64,
            c_int64,
        )
        UDPCallback = CFUNCTYPE(
            None, c_int64, c_char_p, c_char_p, c_int64, c_int64, c_int64, c_int64
        )
        ScriptLogCallback = CFUNCTYPE(None, c_char_p)
        ScriptCodeCallback = CFUNCTYPE(None, c_char_p, c_int64)
    else:
        # 32位环境 - Go语言回调函数声明
        TcpCallback = CFUNCTYPE(
            None, c_int, c_char_p, c_char_p, c_int, c_int, c_int, c_int, c_int, c_int
        )
        HttpCallback = CFUNCTYPE(
            None, c_int, c_int, c_int, c_int, c_char_p, c_char_p, c_char_p, c_int
        )
        WsCallback = CFUNCTYPE(
            None, c_int, c_int, c_int, c_int, c_char_p, c_char_p, c_int, c_int
        )
        UDPCallback = CFUNCTYPE(
            None, c_int, c_char_p, c_char_p, c_int, c_int, c_int, c_int
        )
        ScriptLogCallback = CFUNCTYPE(None, c_char_p)
        ScriptCodeCallback = CFUNCTYPE(None, c_char_p, c_int)

except Exception as e:
    print(f"载入库文件失败: {e}")
    print(f"当前操作系统: {platform.system()}")
    print(f"当前架构: {'64位' if __RuntimeEnvironment else '32位'}")
    print(f"尝试加载: {lib_path if 'lib_path' in locals() else '未知路径'}")
    print("\n提示:")
    if platform.system().lower() == "linux":
        print("  - Linux系统需要 .so 文件 (例如: SunnyNet64.so)")
        print("  - 请确保库文件存在于以下位置之一:")
        print(f"    1. {__module_dir}")
        print(f"    2. {os.getcwd()}")
        print("  - 如果库文件不存在，请联系开发者获取Linux版本")
    elif platform.system().lower() == "darwin":
        print("  - macOS系统需要 .dylib 文件 (例如: SunnyNet64.dylib)")
    else:
        print("  - Windows系统需要 .dll 文件 (例如: SunnyNet64.dll)")
    exit(1)


# 这个类 是动态加载DLL时 设置返回值为指针
class LibSunny:
    def __getattr__(self, name):
        func = getattr(lib, name)
        func.restype = ctypes.POINTER(ctypes.c_int)
        return func


DLLSunny = LibSunny()


# 指针到字节数组 ptr=指针 skip=偏移数 num=取出几个字节
def PtrToByte(ptr, skip, num) -> bytearray | bytes:
    result_as_int = ctypes.cast(ptr, ctypes.c_void_p).value
    if result_as_int == None:
        return bytearray()
    result_as_int += skip
    new_result_ptr = ctypes.cast(result_as_int, ctypes.POINTER(ctypes.c_int))
    buffer = ctypes.create_string_buffer(num)
    ctypes.memmove(buffer, new_result_ptr, num)
    return buffer.raw


# 指针到整数
def PtrToInt(ptr) -> int:
    if isinstance(ptr, int):
        return ptr
    try:
        pp = ctypes.cast(ptr, ctypes.c_void_p)
        if pp.value is None:  # 检查值是否为 None
            return 0
        return int(pp.value)
    except:
        raise TypeError(
            f"module name must be str, not {type(ptr)}",
            ctypes.cast(ptr, ctypes.c_void_p),
        )


# 指针到字符串
def PointerToText(ptr) -> str:
    if ptr == 0:
        return ""
    buff = b""
    i = 0
    while True:
        bs = PtrToByte(ptr, i, 1)
        i += 1
        if len(bs) == 0:
            break
        if bs[0] == 0:
            break
        buff = buff + bs

    DLLSunny.Free(
        ptr
    )  # 释放Sunny的指针,只要是Sunny返回的bytes 或 string 都需要释放指针
    try:
        return buff.decode("utf-8")
    except:
        return buff.decode("gbk")


# 字节数组到字符串
def BytesToText(buff) -> str:
    try:
        return buff.decode("utf-8")
    except:
        return buff.decode("gbk")


# 指针到字节数组 (DLL协商的前8个字节是长度)
def PointerToBytes(ptr) -> bytearray:
    if ptr == 0:
        return bytearray()
    lp = PtrToByte(ptr, 0, 8)
    if len(lp) != 8:
        return lp
    Lxp = PtrToInt(DLLSunny.BytesToInt(create_string_buffer(lp), 8))
    m = PtrToByte(ptr, 8, Lxp)
    DLLSunny.Free(
        ptr
    )  # 释放Sunny的指针,只要是Sunny返回的bytes 或 string 都需要释放指针
    return m
