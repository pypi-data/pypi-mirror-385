import io
import os
import random
import datetime

from unittest import TestCase
import msg2bytes


class TestMsg2bytes(TestCase):
    def test1(self):
        buf = io.BytesIO()
        msg2bytes.write_size(0, buf)
        assert buf.getvalue() == b"\x00"

    def test2(self):
        buf = io.BytesIO()
        msg2bytes.write_size(1, buf)
        assert buf.getvalue() == b"\x01"

    def test3(self):
        buf = io.BytesIO()
        msg2bytes.write_size(126, buf)
        assert buf.getvalue() == b"\x7e"

    def test4(self):
        buf = io.BytesIO()
        msg2bytes.write_size(127, buf)
        assert buf.getvalue() == b"\x7f"

    def test5(self):
        buf = io.BytesIO()
        msg2bytes.write_size(128, buf)
        assert buf.getvalue() == b"\x81\x00"

    def test6(self):
        buf = io.BytesIO()
        msg2bytes.write_size(129, buf)
        assert buf.getvalue() == b"\x81\x01"

    def test7(self):
        buf = io.BytesIO()
        msg2bytes.write_size(16128, buf)
        assert buf.getvalue() == b"\xfe\x00"

    def test8(self):
        buf = io.BytesIO()
        msg2bytes.write_size(16129, buf)
        assert buf.getvalue() == b"\xfe\x01"

    def test9(self):
        buf = io.BytesIO()
        msg2bytes.write_size(16130, buf)
        assert buf.getvalue() == b"\xfe\x02"

    def test10(self):
        buf = io.BytesIO()
        msg2bytes.write_size(16257, buf)
        assert buf.getvalue() == b"\xff\x01"

    def test11(self):
        buf = io.BytesIO()
        msg2bytes.write_size(2064639, buf)
        assert buf.getvalue() == b"\xfe\x81\x7f"

    def test12(self):
        buf = io.BytesIO()
        msg2bytes.write_size(2097151, buf)
        assert buf.getvalue() == b"\xff\xff\x7f"

    def test13(self):
        for i in range(0, 1024):
            buf = io.BytesIO()
            msg2bytes.write_size(i, buf)
            buf.seek(0)
            j = msg2bytes.read_size(buf)
            assert i == j
        for i in range(0, 1024 * 1024 * 1024, 23579):
            buf = io.BytesIO()
            msg2bytes.write_size(i, buf)
            buf.seek(0)
            j = msg2bytes.read_size(buf)
            assert i == j
        for i in range(0, 1024 * 1024 * 1024, 24680):
            buf = io.BytesIO()
            msg2bytes.write_size(i, buf)
            buf.seek(0)
            j = msg2bytes.read_size(buf)
            assert i == j

    def test14(self):
        for _ in range(1024):
            size = random.randint(0, 1024)
            data1 = os.urandom(size)
            data2 = msg2bytes.dumps(data1)
            data3 = msg2bytes.loads(data2)
            assert data1 == data3

    def test15(self):
        data1 = None
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        assert data1 == data3

    def test16(self):
        data1 = True
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        assert data1 == data3

    def test17(self):
        data1 = False
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        assert data1 == data3

    def test18(self):
        data1 = "hello world"
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        assert data1 == data3

    def test19(self):
        data1 = b"hello world"
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        assert data1 == data3

    def test20(self):
        data1 = 0
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        assert data1 == data3

    def test21(self):
        data1 = 1
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        assert data1 == data3

    def test22(self):
        data1 = -1
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        assert data1 == data3

    def test23(self):
        data1 = 128
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        assert data1 == data3

    def test24(self):
        data1 = -128
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        assert data1 == data3

    def test25(self):
        data1 = msg2bytes.uint64(2**64 - 1)
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        assert data1 == data3

    def test26(self):
        data1 = 3.12
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        self.assertAlmostEqual(data1, data3)

    def test27(self):
        data1 = msg2bytes.MAX_FLOAT
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        self.assertAlmostEqual(data1, data3)

    def test28(self):
        data1 = msg2bytes.MIN_FLOAT
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        self.assertAlmostEqual(data1, data3)

    def test29(self):
        data1 = -msg2bytes.MAX_FLOAT
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        self.assertAlmostEqual(data1, data3)

    def test30(self):
        data1 = -msg2bytes.MIN_FLOAT
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        self.assertAlmostEqual(data1, data3)

    def test31(self):
        data1 = [1, 2, 3]
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        self.assertAlmostEqual(data1, data3)

    def test32(self):
        data1 = set([1, 2, 3])
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        self.assertAlmostEqual(data1, data3)

    def test33(self):
        data1 = tuple([1, 2, 3])
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        self.assertAlmostEqual(data1, data3)

    def test34(self):
        data1 = {
            "a": "a",
            "b": "b",
        }
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        self.assertAlmostEqual(data1, data3)

    def test35(self):
        data1 = {"a": "a", "b": b"b", "c": [1, 2, 3], "d": {"e": "e"}}
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        assert data1 == data3

    def test36(self):
        class A(object):
            pass

        data1 = A()
        with self.assertRaises(msg2bytes.NoDumpCodecFound):
            data2 = msg2bytes.dumps(data1)
            data3 = msg2bytes.loads(data2)

    def test37(self):
        data1 = os.urandom(1024)
        file1 = msg2bytes.File()
        with open(file1.filepath, "wb") as fobj:
            fobj.write(data1)
        data2 = msg2bytes.dumps(file1)
        file2 = msg2bytes.loads(data2)
        assert file1.filename == file2.filename
        assert file1.filesize == file2.filesize
        assert file1.filepath != file2.filepath

        with open(file1.filepath, "rb") as fobj:
            file1content = fobj.read()
        with open(file1.filepath, "rb") as fobj:
            file2content = fobj.read()
        assert file1content == file2content

        os.unlink(file1.filepath)
        os.unlink(file2.filepath)

    def test38(self):
        data1 = datetime.datetime.now().date()
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        assert data1 == data3

    def test39(self):
        data1 = datetime.datetime.now().time()
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        assert data1 == data3

    def test40(self):
        today = datetime.datetime.now()
        data1 = {
            "datetime": today,
            "date": today.date(),
            "time": today.time(),
        }
        data2 = msg2bytes.dumps(data1)
        data3 = msg2bytes.loads(data2)
        assert data1 == data3
