import os
import sys
import uuid
import struct
import datetime
import binascii
import tempfile
from io import BytesIO
from decimal import Decimal

from dateutil.parser import parse as datetime_parse

__all__ = [
    "LIST",
    "SET",
    "TUPLE",
    "DICT",
    "NONE",
    "BOOLEAN",
    "TRUE",
    "FALSE",
    "STR",
    "BYTES",
    "DATETIME",
    "DECIMAL",
    "DATE",
    "TIME",
    "INT",
    "INT8",
    "INT16",
    "INT32",
    "INT64",
    "UINT8",
    "UINT16",
    "UINT32",
    "UINT64",
    "BIGINT",
    "FLOAT",
    "SINGLE",
    "DOUBLE",
    "BIGFLOAT",
    "MAX_INT8",
    "MAX_INT16",
    "MAX_INT32",
    "MAX_INT64",
    "MAX_FLOAT",
    "MIN_FLOAT",
    "int8",
    "int16",
    "int32",
    "int64",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
    "bigint",
    "File",
    "Msg2bytesCodec",
    "StrCodec",
    "BytesCodec",
    "ListCodec",
    "SetCodec",
    "TupleCodec",
    "DictCodec",
    "BooleanCodec",
    "TrueCodec",
    "FalseCodec",
    "DatetimeCodec",
    "DateCodec",
    "TimeCodec",
    "DecimalCodec",
    "FileCodec",
    "Int8Codec",
    "Int16Codec",
    "Int32Codec",
    "Int64Codec",
    "Uint8Codec",
    "Uint16Codec",
    "Uint32Codec",
    "Uint64Codec",
    "BigIntCodec",
    "IntCodec",
    "DoubleCodec",
    "BigFloatCodec",
    "FloatCodec",
    "NoDumpCodecFound",
    "NoLoadCodecFound",
    "CodecReadFailed",
    "register_codec",
    "register_dump_codec",
    "register_load_codec",
    "get_dump_codec",
    "get_load_codec",
    "msg2bytes_dump",
    "msg2bytes_load",
    "msg2bytes_load_all",
    "msg2bytes_dumps",
    "msg2bytes_loads_all",
    "msg2bytes_async_dump",
    "msg2bytes_async_load",
    "msg2bytes_async_load_all",
    "read_size",
    "write_size",
    "dump",
    "load",
    "load_all",
    "dumps",
    "loads",  # alias to msg2bytes_loads_all
    "loads_all",  # alias to msg2bytes_loads_all
    "async_read_size",
    "async_write_size",
    "async_dump",
    "async_load",
    "async_load_all",
]

LIST = bytes([1])
SET = bytes([2])
TUPLE = bytes([3])
DICT = bytes([4])

NONE = bytes([5])
BOOLEAN = bytes([6])
TRUE = bytes([7])
FALSE = bytes([8])

STR = bytes([9])
BYTES = bytes([10])
DATETIME = bytes([11])
DECIMAL = bytes([12])
FILE = bytes([13])
DATE = bytes([14])  # v0.1.3引入
TIME = bytes([15])  # v0.1.3引入

INT = bytes([20])  # 抽象类型。实际不会使用的编码code。
INT8 = bytes([21])
INT16 = bytes([22])
INT32 = bytes([23])
INT64 = bytes([24])
UINT8 = bytes([25])
UINT16 = bytes([26])
UINT32 = bytes([27])
UINT64 = bytes([28])
BIGINT = bytes([29])
FLOAT = bytes([30])  # 抽象类型。实际不会使用的编码code。
SINGLE = bytes([31])
DOUBLE = bytes([32])
BIGFLOAT = bytes([33])


MAX_INT8 = 2**7 - 1
MAX_INT16 = 2**15 - 1
MAX_INT32 = 2**31 - 1
MAX_INT64 = 2**63 - 1

MAX_FLOAT = sys.float_info.max
MIN_FLOAT = sys.float_info.min


def write_size(size, wfile):
    if size < 128:
        wfile.write(size.to_bytes(length=1, byteorder="big"))
    elif size < 16384:
        wfile.write(((size // 128) | 0x80).to_bytes(length=1, byteorder="big"))
        wfile.write((size % 128).to_bytes(length=1, byteorder="big"))
    else:
        ds = []
        while size:
            ds.append(size % 128)
            size //= 128
        ds.reverse()
        for i in range(0, len(ds) - 1):
            ds[i] += 128
        wfile.write(bytes(ds))


async def async_write_size(size, wfile):
    if size < 128:
        await wfile.write(size.to_bytes(length=1, byteorder="big"))
    elif size < 16384:
        await wfile.write(((size // 128) | 0x80).to_bytes(length=1, byteorder="big"))
        await wfile.write((size % 128).to_bytes(length=1, byteorder="big"))
    else:
        ds = []
        while size:
            ds.append(size % 128)
            size //= 128
        ds.reverse()
        for i in range(0, len(ds) - 1):
            ds[i] += 128
        await wfile.write(bytes(ds))


def read_size(rfile):
    size = 0
    while True:
        d = rfile.read(1)
        d = ord(d)
        if d > 127:
            size = size * 128 + d - 128
        else:
            size = size * 128 + d
            break
    return size


async def async_read_size(rfile):
    size = 0
    while True:
        d = await rfile.read(1)
        d = ord(d)
        if d > 127:
            size = size * 128 + d - 128
        else:
            size = size * 128 + d
            break
    return size


class int8(int):
    pass


class int16(int):
    pass


class int32(int):
    pass


class int64(int):
    pass


class bigint(int):
    pass


class uint8(int):
    pass


class uint16(int):
    pass


class uint32(int):
    pass


class uint64(int):
    pass


class File(object):
    def __init__(self, root=None, filename=None, filepath=None):
        tmpfilename = uuid.uuid4().hex
        self.root = root or tempfile.gettempdir()
        self.filename = filename or tmpfilename
        self.filepath = filepath or os.path.join(self.root, tmpfilename)

    @property
    def filesize(self):
        if not os.path.exists(self.filepath):
            return 0
        return os.stat(self.filepath).st_size

    def download_content(self, rfile, size):
        """从输入流中读取文件内容，并写入文件中。"""
        with open(self.filepath, "wb") as fobj:
            while size:
                data = rfile.read(4096)
                if not data:
                    break
                fobj.write(data)

    def upload_content(self, wfile):
        """从文件中读取内容，并写入输出流。"""
        with open(self.filepath, "rb") as fobj:
            while True:
                data = fobj.read(4096)
                if not data:
                    break
                wfile.write(data)

    async def async_download_content(self, rfile, size):
        """从输入流中读取文件内容，并写入文件中。"""
        with open(self.filepath, "wb") as fobj:
            while size:
                data = await rfile.read(4096)  # @todo 文件读写的协程化
                if not data:
                    break
                fobj.write(data)

    async def async_upload_content(self, wfile):
        """从文件中读取内容，并写入输出流。"""
        with open(self.filepath, "rb") as fobj:
            while True:
                data = fobj.read(4096)  # @todo 文件读写的协程化
                if not data:
                    break
                await wfile.write(data)


class Msg2bytesCodec(object):
    encoding = "utf-8"

    @classmethod
    def get_encoding(cls, **kwargs):
        return kwargs.get("encoding", cls.encoding)

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        pass

    @classmethod
    def load(cls, rfile, **kwargs):
        pass

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        pass

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        pass


class NoneCodec(Msg2bytesCodec):
    type = type(None)
    code = NONE

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        wfile.write(cls.code)

    @classmethod
    def load(cls, rfile, **kwargs):
        return None

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        await wfile.write(cls.code)

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        return None


class BooleanCodec(Msg2bytesCodec):
    type = bool
    code = BOOLEAN

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        if data is True:
            TrueCodec.dump(data, wfile, **kwargs)
        else:
            FalseCodec.dump(data, wfile, **kwargs)

    @classmethod
    def load(cls, rfile, **kwargs):
        return None

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        if data is True:
            await TrueCodec.async_dump(data, wfile, **kwargs)
        else:
            await FalseCodec.async_dump(data, wfile, **kwargs)

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        return None


class TrueCodec(Msg2bytesCodec):
    type = bool
    code = TRUE

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        wfile.write(cls.code)

    @classmethod
    def load(cls, rfile, **kwargs):
        return True

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        await wfile.write(cls.code)

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        return True


class FalseCodec(Msg2bytesCodec):
    type = bool
    code = FALSE

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        wfile.write(cls.code)

    @classmethod
    def load(cls, rfile, **kwargs):
        return False

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        await wfile.write(cls.code)

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        return False


class StrCodec(Msg2bytesCodec):
    type = str
    code = STR

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        data = data.encode(encoding)
        wfile.write(cls.code)
        write_size(len(data), wfile)
        wfile.write(data)

    @classmethod
    def load(cls, rfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        size = read_size(rfile)
        data = rfile.read(size)
        return data.decode(encoding)

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        data = data.encode(encoding)
        await wfile.write(cls.code)
        await async_write_size(len(data), wfile)
        await wfile.write(data)

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        size = await async_read_size(rfile)
        data = await rfile.read(size)
        return data.decode(encoding)


class BytesCodec(Msg2bytesCodec):
    type = bytes
    code = BYTES

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        wfile.write(cls.code)
        write_size(len(data), wfile)
        wfile.write(data)

    @classmethod
    def load(cls, rfile, **kwargs):
        size = read_size(rfile)
        return rfile.read(size)

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        await wfile.write(cls.code)
        await async_write_size(len(data), wfile)
        await wfile.write(data)

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        size = await async_read_size(rfile)
        return await rfile.read(size)


class ListCodec(Msg2bytesCodec):
    type = list
    code = LIST

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        wfile.write(cls.code)
        write_size(len(data), wfile)
        for item in data:
            msg2bytes_dump(item, wfile, **kwargs)

    @classmethod
    def load(cls, rfile, **kwargs):
        data = []
        size = read_size(rfile)
        for _ in range(size):
            item = msg2bytes_load(rfile, **kwargs)
            data.append(item)
        return data

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        await wfile.write(cls.code)
        await async_write_size(len(data), wfile)
        for item in data:
            await msg2bytes_async_dump(item, wfile, **kwargs)

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        data = []
        size = await async_read_size(rfile)
        for _ in range(size):
            item = await msg2bytes_async_load(rfile, **kwargs)
            data.append(item)
        return data


class SetCodec(Msg2bytesCodec):
    type = set
    code = SET

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        wfile.write(cls.code)
        write_size(len(data), wfile)
        for item in data:
            msg2bytes_dump(item, wfile, **kwargs)

    @classmethod
    def load(cls, rfile, **kwargs):
        data = set()
        size = read_size(rfile)
        for _ in range(size):
            item = msg2bytes_load(rfile, **kwargs)
            data.add(item)
        return data

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        await wfile.write(cls.code)
        await async_write_size(len(data), wfile)
        for item in data:
            await msg2bytes_async_dump(item, wfile, **kwargs)

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        data = set()
        size = await async_read_size(rfile)
        for _ in range(size):
            item = await msg2bytes_async_load(rfile, **kwargs)
            data.add(item)
        return data


class TupleCodec(Msg2bytesCodec):
    type = tuple
    code = TUPLE

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        wfile.write(cls.code)
        write_size(len(data), wfile)
        for item in data:
            msg2bytes_dump(item, wfile, **kwargs)

    @classmethod
    def load(cls, rfile, **kwargs):
        data = []
        size = read_size(rfile)
        for _ in range(size):
            item = msg2bytes_load(rfile, **kwargs)
            data.append(item)
        return tuple(data)

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        await wfile.write(cls.code)
        await async_write_size(len(data), wfile)
        for item in data:
            await msg2bytes_async_dump(item, wfile, **kwargs)

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        data = []
        size = await async_read_size(rfile)
        for _ in range(size):
            item = await msg2bytes_async_load(rfile, **kwargs)
            data.append(item)
        return tuple(data)


class DictCodec(Msg2bytesCodec):
    type = dict
    code = DICT

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        wfile.write(cls.code)
        write_size(len(data), wfile)
        for k, v in data.items():
            msg2bytes_dump(k, wfile, **kwargs)
            msg2bytes_dump(v, wfile, **kwargs)

    @classmethod
    def load(cls, rfile, **kwargs):
        data = {}
        size = read_size(rfile)
        for _ in range(size):
            k = msg2bytes_load(rfile, **kwargs)
            v = msg2bytes_load(rfile, **kwargs)
            data[k] = v
        return data

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        await wfile.write(cls.code)
        await async_write_size(len(data), wfile)
        for k, v in data.items():
            await msg2bytes_async_dump(k, wfile, **kwargs)
            await msg2bytes_async_dump(v, wfile, **kwargs)

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        data = {}
        size = await async_read_size(rfile)
        for _ in range(size):
            k = await msg2bytes_async_load(rfile, **kwargs)
            v = await msg2bytes_async_load(rfile, **kwargs)
            data[k] = v
        return data


class DatetimeCodec(Msg2bytesCodec):
    type = datetime.datetime
    code = DATETIME

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        data = data.isoformat().encode(encoding)
        wfile.write(cls.code)
        write_size(len(data), wfile)
        wfile.write(data)

    @classmethod
    def load(cls, rfile, **kwargs):
        size = read_size(rfile)
        data = rfile.read(size)
        return datetime_parse(data)

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        data = data.isoformat().encode(encoding)
        await wfile.write(cls.code)
        await async_write_size(len(data), wfile)
        await wfile.write(data)

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        size = await async_read_size(rfile)
        data = await rfile.read(size)
        return datetime_parse(data)


class DateCodec(Msg2bytesCodec):
    type = datetime.date
    code = DATE

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        data = data.isoformat().encode(encoding)
        wfile.write(cls.code)
        write_size(len(data), wfile)
        wfile.write(data)

    @classmethod
    def load(cls, rfile, **kwargs):
        size = read_size(rfile)
        data = rfile.read(size)
        return datetime_parse(data).date()

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        data = data.isoformat().encode(encoding)
        await wfile.write(cls.code)
        await async_write_size(len(data), wfile)
        await wfile.write(data)

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        size = await async_read_size(rfile)
        data = await rfile.read(size)
        return datetime_parse(data).date()


class TimeCodec(Msg2bytesCodec):
    type = datetime.time
    code = TIME

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        data = data.isoformat().encode(encoding)
        wfile.write(cls.code)
        write_size(len(data), wfile)
        wfile.write(data)

    @classmethod
    def load(cls, rfile, **kwargs):
        size = read_size(rfile)
        data = rfile.read(size)
        return datetime_parse(data).time()

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        data = data.isoformat().encode(encoding)
        await wfile.write(cls.code)
        await async_write_size(len(data), wfile)
        await wfile.write(data)

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        size = await async_read_size(rfile)
        data = await rfile.read(size)
        return datetime_parse(data).time()


class DecimalCodec(Msg2bytesCodec):
    type = Decimal
    code = DECIMAL

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        data = str(data).encode(encoding)
        wfile.write(cls.code)
        write_size(len(data), wfile)
        wfile.write(data)

    @classmethod
    def load(cls, rfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        size = read_size(rfile)
        data = rfile.read(size).decode(encoding)
        return Decimal(data)

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        data = str(data).encode(encoding)
        await wfile.write(cls.code)
        await async_write_size(len(data), wfile)
        await wfile.write(data)

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        size = await async_read_size(rfile)
        data = await rfile.read(size).decode(encoding)
        return Decimal(data)


class FileCodec(Msg2bytesCodec):
    type = File
    code = FILE

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        wfile.write(cls.code)
        msg2bytes_dump(data.filename, wfile, **kwargs)
        msg2bytes_dump(data.filesize, wfile, **kwargs)
        data.upload_content(wfile)

    @classmethod
    def load(cls, rfile, **kwargs):
        data = File()
        data.filename = msg2bytes_load(rfile, **kwargs)
        size = msg2bytes_load(rfile, **kwargs)
        data.download_content(rfile, size)
        return data

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        await wfile.write(cls.code)
        await msg2bytes_dump(data.filename, wfile, **kwargs)
        await msg2bytes_dump(data.filesize, wfile, **kwargs)
        await data.async_upload_content(wfile)

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        data = File()
        data.filename = await msg2bytes_async_load(rfile, **kwargs)
        size = await msg2bytes_async_load(rfile, **kwargs)
        await data.async_download_content(rfile, size)
        return data


class IntCodec(Msg2bytesCodec):
    type = int
    code = INT

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        """根据数值大小，自动选择合适的类型进行编码。"""
        if data > MAX_INT64 or data < -MAX_INT64:
            BigIntCodec.dump(data, wfile, **kwargs)
        elif data > MAX_INT32 or data < -MAX_INT32:
            Int64Codec.dump(data, wfile, **kwargs)
        elif data > MAX_INT16 or data < -MAX_INT16:
            Int32Codec.dump(data, wfile, **kwargs)
        elif data > MAX_INT8 or data < -MAX_INT8:
            Int16Codec.dump(data, wfile, **kwargs)
        else:
            Int8Codec.dump(data, wfile, **kwargs)

    @classmethod
    def load(cls, rfile, **kwargs):
        """不允许使用抽象类型进行编码，所以无法进行解码。"""
        pass

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        """根据数值大小，自动选择合适的类型进行编码。"""
        if data > MAX_INT64 or data < -MAX_INT64:
            await BigIntCodec.async_dump(data, wfile, **kwargs)
        elif data > MAX_INT32 or data < -MAX_INT32:
            await Int64Codec.async_dump(data, wfile, **kwargs)
        elif data > MAX_INT16 or data < -MAX_INT16:
            await Int32Codec.async_dump(data, wfile, **kwargs)
        elif data > MAX_INT8 or data < -MAX_INT8:
            await Int16Codec.async_dump(data, wfile, **kwargs)
        else:
            await Int8Codec.async_dump(data, wfile, **kwargs)

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        """不允许使用抽象类型进行编码，所以无法进行解码。"""
        pass


class Int8Codec(Msg2bytesCodec):
    type = int8
    code = INT8

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        wfile.write(cls.code)
        wfile.write(struct.pack(">b", data))

    @classmethod
    def load(cls, rfile, **kwargs):
        data = rfile.read(1)
        return struct.unpack(">b", data)[0]

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        await wfile.write(cls.code)
        await wfile.write(struct.pack(">b", data))

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        data = await rfile.read(1)
        return struct.unpack(">b", data)[0]


class Int16Codec(Msg2bytesCodec):
    type = int16
    code = INT16

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        wfile.write(cls.code)
        wfile.write(struct.pack(">h", data))

    @classmethod
    def load(cls, rfile, **kwargs):
        data = rfile.read(2)
        return struct.unpack(">h", data)[0]

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        await wfile.write(cls.code)
        await wfile.write(struct.pack(">h", data))

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        data = await rfile.read(2)
        return struct.unpack(">h", data)[0]


class Int32Codec(Msg2bytesCodec):
    type = int32
    code = INT32

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        wfile.write(cls.code)
        wfile.write(struct.pack(">i", data))

    @classmethod
    def load(cls, rfile, **kwargs):
        data = rfile.read(4)
        return struct.unpack(">i", data)[0]

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        await wfile.write(cls.code)
        await wfile.write(struct.pack(">i", data))

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        data = await rfile.read(4)
        return struct.unpack(">i", data)[0]


class Int64Codec(Msg2bytesCodec):
    type = int64
    code = INT64

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        wfile.write(cls.code)
        wfile.write(struct.pack(">q", data))

    @classmethod
    def load(cls, rfile, **kwargs):
        data = rfile.read(8)
        return struct.unpack(">q", data)[0]

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        await wfile.write(cls.code)
        await wfile.write(struct.pack(">q", data))

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        data = await rfile.read(8)
        return struct.unpack(">q", data)[0]


class Uint8Codec(Msg2bytesCodec):
    type = uint8
    code = UINT8

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        wfile.write(cls.code)
        wfile.write(struct.pack(">B", data))

    @classmethod
    def load(cls, rfile, **kwargs):
        data = rfile.read(1)
        return struct.unpack(">B", data)[0]

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        await wfile.write(cls.code)
        await wfile.write(struct.pack(">B", data))

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        data = await rfile.read(1)
        return struct.unpack(">B", data)[0]


class Uint16Codec(Msg2bytesCodec):
    type = uint16
    code = UINT16

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        wfile.write(cls.code)
        wfile.write(struct.pack(">H", data))

    @classmethod
    def load(cls, rfile, **kwargs):
        data = rfile.read(2)
        return struct.unpack(">H", data)[0]

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        await wfile.write(cls.code)
        await wfile.write(struct.pack(">H", data))

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        data = await rfile.read(2)
        return struct.unpack(">H", data)[0]


class Uint32Codec(Msg2bytesCodec):
    type = uint32
    code = UINT32

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        wfile.write(cls.code)
        wfile.write(struct.pack(">I", data))

    @classmethod
    def load(cls, rfile, **kwargs):
        data = rfile.read(4)
        return struct.unpack(">I", data)[0]

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        await wfile.write(cls.code)
        await wfile.write(struct.pack(">I", data))

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        data = await rfile.read(4)
        return struct.unpack(">I", data)[0]


class Uint64Codec(Msg2bytesCodec):
    type = uint64
    code = UINT64

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        wfile.write(cls.code)
        wfile.write(struct.pack(">Q", data))

    @classmethod
    def load(cls, rfile, **kwargs):
        data = rfile.read(8)
        return struct.unpack(">Q", data)[0]

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        await wfile.write(cls.code)
        await wfile.write(struct.pack(">Q", data))

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        data = await rfile.read(8)
        return struct.unpack(">Q", data)[0]


class BigIntCodec(Msg2bytesCodec):
    type = bigint
    code = BIGINT

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        data = str(data).encode(encoding)
        wfile.write(cls.code)
        write_size(len(data), wfile)
        wfile.write(data)

    @classmethod
    def load(cls, rfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        size = read_size(rfile)
        data = rfile.read(size).decode(encoding)
        return int(data)

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        data = str(data).encode(encoding)
        await wfile.write(cls.code)
        await async_write_size(len(data), wfile)
        await wfile.write(data)

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        size = await async_read_size(rfile)
        data = await rfile.read(size).decode(encoding)
        return int(data)


class FloatCodec(Msg2bytesCodec):
    type = float
    code = FLOAT

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        if (data > 0 and (data > MAX_FLOAT or data < MIN_FLOAT)) or (
            data < 0 and (data < -MAX_FLOAT or data > -MIN_FLOAT)
        ):
            return BigFloatCodec.dump(data, wfile, **kwargs)
        else:
            return DoubleCodec.dump(data, wfile, **kwargs)

    @classmethod
    def load(cls, rfile, **kwargs):
        pass

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        if (data > 0 and (data > MAX_FLOAT or data < MIN_FLOAT)) or (
            data < 0 and (data < -MAX_FLOAT or data > -MIN_FLOAT)
        ):
            await BigFloatCodec.async_dump(data, wfile, **kwargs)
        else:
            await DoubleCodec.async_dump(data, wfile, **kwargs)

    @classmethod
    def load(cls, rfile, **kwargs):
        pass


class SingleCodec(Msg2bytesCodec):
    """单精度浮点数。

    对于python下的float类型数据，全部按double进行序列化。
    保留这个，可以用来处理来自其它语言的单精度数据的反序列化。
    """

    type = float
    code = SINGLE

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        wfile.write(cls.code)
        wfile.write(struct.pack(">f", data))

    @classmethod
    def load(cls, rfile, **kwargs):
        data = rfile.read(4)
        return struct.unpack(">f", data)[0]

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        await wfile.write(cls.code)
        await wfile.write(struct.pack(">f", data))

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        data = await rfile.read(4)
        return struct.unpack(">f", data)[0]


class DoubleCodec(Msg2bytesCodec):
    type = float
    code = DOUBLE

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        wfile.write(cls.code)
        wfile.write(struct.pack(">d", data))

    @classmethod
    def load(cls, rfile, **kwargs):
        data = rfile.read(8)
        return struct.unpack(">d", data)[0]

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        await wfile.write(cls.code)
        await wfile.write(struct.pack(">d", data))

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        data = await rfile.read(8)
        return struct.unpack(">d", data)[0]


class BigFloatCodec(Msg2bytesCodec):
    type = float
    code = BIGFLOAT

    @classmethod
    def dump(cls, data, wfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        data = str(data).encode(encoding)
        wfile.write(cls.code)
        write_size(len(data), wfile)
        wfile.write(data)

    @classmethod
    def load(cls, rfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        size = read_size(rfile)
        data = rfile.read(size).decode(encoding)
        return float(data)

    @classmethod
    async def async_dump(cls, data, wfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        data = str(data).encode(encoding)
        await wfile.write(cls.code)
        await async_write_size(len(data), wfile)
        await wfile.write(data)

    @classmethod
    async def async_load(cls, rfile, **kwargs):
        encoding = cls.get_encoding(**kwargs)
        size = await async_read_size(rfile)
        data = await rfile.read(size).decode(encoding)
        return float(data)


class __NoCodec(object):
    pass


_NoCodec = __NoCodec()


class NoDumpCodecFound(RuntimeError):
    """没有相应数据类型的编码器。"""

    pass


class NoLoadCodecFound(RuntimeError):
    """没有相应数据类型的解码器。"""

    pass


class CodecReadFailed(RuntimeError):
    """读取数据内容失败。"""

    pass


_msg2bytes_dump_codecs = {}
_msg2bytes_load_codecs = {}


def register_codec(codec, type=None, code=None):
    type = type or codec.type
    code = code or codec.code
    _msg2bytes_dump_codecs[type] = codec
    _msg2bytes_load_codecs[code] = codec


def register_dump_codec(codec, type=None):
    type = type or codec.type
    _msg2bytes_dump_codecs[type] = codec


def register_load_codec(codec, code=None):
    code = code or codec.code
    _msg2bytes_load_codecs[code] = codec


def get_dump_codec(value):
    value_type = type(value)
    return _msg2bytes_dump_codecs.get(value_type, _NoCodec)


def get_load_codec(code):
    return _msg2bytes_load_codecs.get(code, _NoCodec)


register_codec(NoneCodec)
register_codec(ListCodec)
register_codec(SetCodec)
register_codec(TupleCodec)
register_codec(DictCodec)

register_codec(StrCodec)
register_codec(BytesCodec)
register_codec(DatetimeCodec)
register_codec(DecimalCodec)
register_codec(DateCodec)  # v0.1.3引入
register_codec(TimeCodec)  # v0.1.3引入

register_codec(TrueCodec)
register_codec(FalseCodec)
register_codec(BooleanCodec)  # 必须要在所有bool类型编解码器后注册

register_codec(Int8Codec)
register_codec(Int16Codec)
register_codec(Int32Codec)
register_codec(Int64Codec)
register_codec(Uint8Codec)
register_codec(Uint16Codec)
register_codec(Uint32Codec)
register_codec(Uint64Codec)
register_codec(BigIntCodec)
register_codec(IntCodec)  # 必须要在所有int类型编解码器后注册

register_codec(SingleCodec)
register_codec(DoubleCodec)
register_codec(BigFloatCodec)
register_codec(FloatCodec)  # 必须要在所有float类型编解码器后注册

register_codec(FileCodec)


def msg2bytes_dump(value, wfile, **kwargs):
    codec = get_dump_codec(value)
    if codec != _NoCodec:
        codec.dump(value, wfile, **kwargs)
    else:
        raise NoDumpCodecFound("no codec found for type: {}".format(type(value)))


def msg2bytes_load(rfile, **kwargs):
    code = rfile.read(1)
    if not code:
        raise CodecReadFailed()
    codec = get_load_codec(code)
    if codec != _NoCodec:
        return codec.load(rfile, **kwargs)
    else:
        raise NoLoadCodecFound(
            "no codec found for code: 0x{}".format(binascii.hexlify(code))
        )


def msg2bytes_load_all(rfile, **kwargs):
    data = []
    while True:
        try:
            item = msg2bytes_load(rfile, **kwargs)
            data.append(item)
        except CodecReadFailed:
            break
    if len(data) == 1:
        return data[0]
    else:
        return data


def msg2bytes_dumps(value, **kwargs):
    wfile = BytesIO()
    msg2bytes_dump(value, wfile, **kwargs)
    return wfile.getvalue()


def msg2bytes_loads_all(data, **kwargs):
    rfile = BytesIO(data)
    return msg2bytes_load_all(rfile, **kwargs)


async def msg2bytes_async_dump(value, wfile, **kwargs):
    codec = get_dump_codec(value)
    if codec != _NoCodec:
        await codec.async_dump(value, wfile, **kwargs)
    else:
        raise NoDumpCodecFound("no codec found for type: {}".format(type(value)))


async def msg2bytes_async_load(rfile, **kwargs):
    code = await rfile.read(1)
    if not code:
        raise CodecReadFailed()
    codec = get_load_codec(code)
    if codec != _NoCodec:
        return await codec.async_load(rfile, **kwargs)
    else:
        raise NoLoadCodecFound(
            "no codec found for code: 0x{}".format(binascii.hexlify(code))
        )


async def msg2bytes_async_load_all(rfile, **kwargs):
    data = []
    while True:
        try:
            item = await msg2bytes_async_load(rfile, **kwargs)
            data.append(item)
        except CodecReadFailed:
            break
    if len(data) == 1:
        return data[0]
    else:
        return data


dump = msg2bytes_dump
load = msg2bytes_load
load_all = msg2bytes_load_all

dumps = msg2bytes_dumps
loads = msg2bytes_loads_all
loads_all = msg2bytes_loads_all

async_dump = msg2bytes_async_dump
async_load = msg2bytes_async_load
async_load_all = msg2bytes_async_load_all
