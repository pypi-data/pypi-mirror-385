# Copyright (c) 2025 JohnScotttt
# Version pre 0.2.2

__version__ = "pre 0.2.2"

K2_TARGET_VID = 0x0716
K2_TARGET_PID = 0x5060


class metadata:
    def raw(): ...
    def bit_loc(): ...
    def field(): ...
    def value(): ...


class WITRN_DEV:
    """
    The default parameters will be directly connected to K2.

    If necessary, you can use (vid, pid) or path parameters to connect to the device.

    Debugging mode is only recommended to be enabled when a large amount of 'Error Data' is detected. 
    In this case, the API will raise an exception.
    """

    def __init__(self, *args, debug=False, **kwargs): ...

    def read_data() -> list: ...
    def general_unpack(self, data: list = None) -> tuple[str, metadata]: ...

    def pd_unpack(self,
                  data: list = None,
                  last_pdo: metadata = None,
                  last_ext: metadata = None,
                  last_rdo: metadata = None) -> tuple[str, metadata]: ...

    def auto_unpack(self,
                    data: list = None,
                    last_pdo: metadata = None,
                    last_ext: metadata = None,
                    last_rdo: metadata = None) -> tuple[str, metadata]: ...

    def close(self): ...


def is_pdo(msg: metadata) -> bool: ...

def is_rdo(msg: metadata) -> bool: ...

def provide_ext(msg: metadata) -> bool: ...
