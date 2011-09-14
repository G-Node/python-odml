import unittest

import odml.types as typ
import odml
import datetime

class TestTypes(unittest.TestCase):
    def test_date(self):
        date = datetime.date(2011, 12, 1)
        date_string = '2011-12-01'
        self.assertEqual(date, typ.date_get(date_string))
        self.assertEqual(typ.date_set(date), date_string)

    def test_time(self):
        time = datetime.time(12,34,56)
        time_string = '12:34:56'
        self.assertEqual(time, typ.time_get(time_string))
        self.assertEqual(typ.time_set(time), time_string)

    def test_datetime(self):
        date = datetime.datetime(2011, 12, 1, 12, 34, 56)
        date_string = '2011-12-01 12:34:56'
        self.assertEqual(date, typ.datetime_get(date_string))
        self.assertEqual(typ.datetime_set(date), date_string)

    def test_empty_binary(self):
        v = odml.Value("", dtype="string")
        v.dtype = "binary"
        v.encoding = "base64"
        self.assertIsNone(v.value)
        v.encoding = "quoted-printable"
        self.assertIsNone(v.value)
        v.encoding = "hexadecimal"
        self.assertIsNone(v.value)
        self.assertEqual(v.checksum, 'crc32$00000000')
        v.checksum = "md5"
        self.assertEqual(v.checksum, 'md5$d41d8cd98f00b204e9800998ecf8427e')

    def test_8bit_binary(self):
        data = ''.join([chr(i) for i in xrange(256)])
        v = odml.Value(data, dtype="binary")

        v.encoder = "base64"
        b64_data = 'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w==\n'
        self.assertEqual(v.value, b64_data)
        v.value = b64_data
        self.assertEqual(v.data, data)
        self.assertEqual(v.value, b64_data)

        v.encoder = "quoted-printable"
        qp_data = '=00=01=02=03=04=05=06=07=08=09\n=0B=0C\r=0E=0F=10=11=12=13=14=15=16=17=18=19=1A=1B=1C=1D=1E=1F !"#$%&\'()*+,-=\n./0123456789:;<=3D>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuv=\nwxyz{|}~=7F=80=81=82=83=84=85=86=87=88=89=8A=8B=8C=8D=8E=8F=90=91=92=93=94=\n=95=96=97=98=99=9A=9B=9C=9D=9E=9F=A0=A1=A2=A3=A4=A5=A6=A7=A8=A9=AA=AB=AC=AD=\n=AE=AF=B0=B1=B2=B3=B4=B5=B6=B7=B8=B9=BA=BB=BC=BD=BE=BF=C0=C1=C2=C3=C4=C5=C6=\n=C7=C8=C9=CA=CB=CC=CD=CE=CF=D0=D1=D2=D3=D4=D5=D6=D7=D8=D9=DA=DB=DC=DD=DE=DF=\n=E0=E1=E2=E3=E4=E5=E6=E7=E8=E9=EA=EB=EC=ED=EE=EF=F0=F1=F2=F3=F4=F5=F6=F7=F8=\n=F9=FA=FB=FC=FD=FE=FF'
        self.assertEqual(v.value, qp_data)
        v.value = qp_data
        self.assertEqual(v.data, data)
        self.assertEqual(v.value, qp_data)

        v.encoder = "hexadecimal"
        hex_data = '000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f404142434445464748494a4b4c4d4e4f505152535455565758595a5b5c5d5e5f606162636465666768696a6b6c6d6e6f707172737475767778797a7b7c7d7e7f808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9fa0a1a2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b3b4b5b6b7b8b9babbbcbdbebfc0c1c2c3c4c5c6c7c8c9cacbcccdcecfd0d1d2d3d4d5d6d7d8d9dadbdcdddedfe0e1e2e3e4e5e6e7e8e9eaebecedeeeff0f1f2f3f4f5f6f7f8f9fafbfcfdfeff'
        self.assertEqual(v.value, hex_data)
        v.value = hex_data
        self.assertEqual(v.data, data)
        self.assertEqual(v.value, hex_data)

        self.assertEqual(v.checksum, 'crc32$29058c73')
        v.checksum = "md5"
        self.assertEqual(v.checksum, 'md5$e2c865db4162bed963bfaa9ef6ac18f0')
        v.encoder = ''
        v.data = v.data[:127] # chrs > 128 cannot be converted to ascii
        v.dtype = "string"
        self.assertIsNone(v.encoder)
        self.assertIsNone(v.checksum)
        self.assertEqual(v.value, data[:127])

    def test_int(self):
        v = odml.Value("123456789012345678901", dtype="int")
        self.assertEqual(v.data, 123456789012345678901)
        self.assertEqual(v.value, "123456789012345678901")
        v = odml.Value("-123456789012345678901", dtype="int")
        self.assertEqual(v.data, -123456789012345678901)
        v = odml.Value("123.45", dtype="int")
        self.assertEqual(v.data, 123)

if __name__ == '__main__':
    unittest.main()
