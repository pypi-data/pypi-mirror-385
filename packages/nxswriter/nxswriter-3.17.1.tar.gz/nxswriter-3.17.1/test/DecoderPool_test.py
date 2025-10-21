#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
#
#    nexdatas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nexdatas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nexdatas.  If not, see <http://www.gnu.org/licenses/>.
# \package test nexdatas
# \file DecoderPoolTest.py
# unittests for field Tags running Tango Server
#
import unittest
import sys
import struct
import json
import numpy as np
import nxswriter

from nxswriter.DecoderPool import (
    DecoderPool, UTF8decoder, UINT32decoder, VDEOdecoder)


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)

# Wrong Decoder


class W0DS(object):
    pass

# Wrong Decoder


class W1DS(object):
    # constructor

    def __init__(self):
        # name attribute
        self.name = None
        # dtype attribute
        self.dtype = None
        # format attribute
        self.format = None


# Wrong Decoder
class W2DS(object):
    # constructor

    def __init__(self):
        # name attribute
        self.name = None
        # dtype attribute
        self.dtype = None
        # format attribute
        self.format = None

    # load method
    def load(self):
        pass


# Wrong Decoder
class W3DS(object):
    # constructor

    def __init__(self):
        # name attribute
        self.name = None
        # dtype attribute
        self.dtype = None
        # format attribute
        self.format = None

    # load method
    def load(self):
        pass

    # shape method
    def shape(self):
        pass


# Wrong Decoder
class W4DS(object):
    # constructor

    def __init__(self):
        # name attribute
        self.name = None
        # dtype attribute
        self.dtype = None
        # format attribute
        self.format = None

    # load method
    def load(self):
        pass

    # shape method
    def shape(self):
        pass

    # decode method
    def decode(self):
        pass


# test fixture
class DecoderPoolTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._tfname = "doc"
        self._fname = "test.h5"
        self._nxDoc = None
        self._eDoc = None
        self._fattrs = {"short_name": "test", "units": "m"}
        self._gname = "testDoc"
        self._gtype = "NXentry"

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        self.__images = [
            b'YATD\x02\x00@\x00\x02\x00\x00\x00\x05\x00\x00\x00\x00\x00'
            b'\x02\x00\x06\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02'
            b'\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00\x06\x00'
            b'\x07\x00\x08\x00\t\x00\n\x00\x0b\x00\x0c\x00\r\x00\x0e\x00'
            b'\x0f\x00\x10\x00\x11\x00\x12\x00\x13\x00\x14\x00\x15\x00\x16'
            b'\x00\x17\x00',
            b'YATD\x02\x00@\x00\x02\x00\x00\x00\x02\x00\x00\x00\x00\x00'
            b'\x03\x00\x02\x00\x03\x00\x04\x00\x00\x00\x00\x00\x00\x00\x04'
            b'\x00\x00\x00\x08\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00'
            b'\x00\x00\x04\x00\x00\x00\x05\x00\x00\x00\x06\x00\x00\x00\x07'
            b'\x00\x00\x00\x08\x00\x00\x00\t\x00\x00\x00\n\x00\x00\x00\x0b'
            b'\x00\x00\x00\x0c\x00\x00\x00\r\x00\x00\x00\x0e\x00\x00\x00\x0f'
            b'\x00\x00\x00\x10\x00\x00\x00\x11\x00\x00\x00\x12\x00\x00\x00'
            b'\x13\x00\x00\x00\x14\x00\x00\x00\x15\x00\x00\x00\x16\x00\x00'
            b'\x00\x17\x00\x00\x00'
        ]

    # test starter
    # \brief Common set up
    def setUp(self):
        # file handle
        print("\nsetting up...")

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")

    # Exception tester
    # \param exception expected exception
    # \param method called method
    # \param args list with method arguments
    # \param kwargs dictionary with method arguments
    def myAssertRaise(self, exception, method, *args, **kwargs):
        try:
            error = False
            method(*args, **kwargs)
        except Exception:
            error = True
        self.assertEqual(error, True)

    # constructor test
    # \brief It tests default settings
    def test_constructor_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = DecoderPool()
        self.assertTrue(isinstance(el, object))

        el = DecoderPool(json.loads("{}"))
        self.assertTrue(isinstance(el, object))

        jsn = json.loads(
            '{"decoders":{"UTF":"nxswriter.DecoderPool.Decode"}}')
        self.myAssertRaise(AttributeError, DecoderPool, jsn)

        jsn = json.loads('{"decoders":{"UTF":"DDecoderPool.UTF8decoder"}}')
        self.myAssertRaise(ImportError, DecoderPool, jsn)

        el = DecoderPool(
            json.loads(
                '{"decoders":{"UTF":"nxswriter.DecoderPool.UTF8decoder"}}'))

    # hasDecoder test
    # \brief It tests default settings
    def test_hasDecoder(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = DecoderPool()
        self.assertTrue(el.hasDecoder("UTF8"))
        self.assertTrue(el.hasDecoder("UINT32"))
        self.assertTrue(el.hasDecoder("LIMA_VIDEO_IMAGE"))
        self.assertTrue(not el.hasDecoder("DBB"))
        self.assertTrue(not el.hasDecoder("CL"))

        el = DecoderPool(
            json.loads(
                '{"decoders":{"UTF":"nxswriter.DecoderPool.UTF8decoder"}}'))
        self.assertTrue(el.hasDecoder("UTF8"))
        self.assertTrue(el.hasDecoder("UINT32"))
        self.assertTrue(el.hasDecoder("LIMA_VIDEO_IMAGE"))
        self.assertTrue(not el.hasDecoder("DBB"))
        self.assertTrue(el.hasDecoder("UTF"))

    # get method test
    # \brief It tests default settings
    def test_get(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = DecoderPool()
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        ds = el.get("UINT32")
        self.assertTrue(isinstance(ds, UINT32decoder))
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        self.assertEqual(el.get("DDB"), None)
        self.assertEqual(el.get("CL"), None)

        el = DecoderPool(
            json.loads(
                '{"decoders":{"UTF":"nxswriter.DecoderPool.UTF8decoder"}}'))
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        ds = el.get("UINT32")
        self.assertTrue(isinstance(ds, UINT32decoder))
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        self.assertEqual(el.get("DDB"), None)
        ds = el.get("UTF")
        self.assertTrue(isinstance(ds, UTF8decoder))

    # append method test
    # \brief It tests default settings
    def test_append(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = DecoderPool()
        el.append(nxswriter.DecoderPool.UTF8decoder, "UTF")
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        ds = el.get("UINT32")
        self.assertTrue(isinstance(ds, UINT32decoder))
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        self.assertEqual(el.get("DDB"), None)
        ds = el.get("UTF")
        self.assertTrue(isinstance(ds, UTF8decoder))

        el = DecoderPool()
        el.append(W0DS, "W0")
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        ds = el.get("UINT32")
        self.assertTrue(isinstance(ds, UINT32decoder))
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        self.assertEqual(el.get("W0"), None)

        el = DecoderPool()
        el.append(W1DS, "W0")
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        ds = el.get("UINT32")
        self.assertTrue(isinstance(ds, UINT32decoder))
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        self.assertEqual(el.get("W0"), None)

        el = DecoderPool()
        el.append(W2DS, "W0")
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        ds = el.get("UINT32")
        self.assertTrue(isinstance(ds, UINT32decoder))
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        self.assertEqual(el.get("W0"), None)

        el = DecoderPool()
        el.append(W3DS, "W0")
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        ds = el.get("UINT32")
        self.assertTrue(isinstance(ds, UINT32decoder))
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        self.assertEqual(el.get("W0"), None)

        el = DecoderPool()
        el.append(W4DS, "W0")
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        ds = el.get("UINT32")
        self.assertTrue(isinstance(ds, UINT32decoder))
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        dc = el.get("W0")
        self.assertTrue(isinstance(dc, W4DS))

    # append put test
    # \brief It tests default settings
    def test_pop(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = DecoderPool()
        el.pop("CL")
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        ds = el.get("UINT32")
        self.assertTrue(isinstance(ds, UINT32decoder))
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        el.pop("UINT32")
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        self.assertEqual(el.get("UINT32"), None)
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        self.assertEqual(el.get("DDB"), None)
        self.assertEqual(el.get("CL"), None)

        el = DecoderPool()
        el.append(W4DS, "W0")
        ds = el.get("W0")
        self.assertTrue(isinstance(ds, W4DS))
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        ds = el.get("UINT32")
        self.assertTrue(isinstance(ds, UINT32decoder))
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        el.pop("W0")
        el.pop("UINT32")
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        self.assertEqual(el.get("UINT32"), None)
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        self.assertEqual(el.get("DDB"), None)
        self.assertEqual(el.get("W0"), None)

    def test_DATA_ARRAY_decoder(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        w1 = self.__images[0]
        w2 = self.__images[1]
        ad = nxswriter.DecoderPool.DATAARRAYdecoder()

        ad.load(("DATA_ARRAY", w1))
        dw1 = ad.decode()
        tw1 = np.array(range(24), dtype='int16').reshape(4, 6)
        self.assertEqual(dw1.shape, (4, 6))
        self.assertEqual(ad.shape(), [4, 6])
        self.assertTrue(np.allclose(dw1, tw1))

        ad.load(("DATA_ARRAY", w2))
        dw2 = ad.decode()
        tw2 = np.array(range(24), dtype='uint32').reshape(4, 3, 2)
        self.assertEqual(tw2.shape, (4, 3, 2))
        self.assertEqual(ad.shape(), [4, 3, 2])
        self.assertTrue(np.allclose(dw2, tw2))


if __name__ == '__main__':
    unittest.main()
