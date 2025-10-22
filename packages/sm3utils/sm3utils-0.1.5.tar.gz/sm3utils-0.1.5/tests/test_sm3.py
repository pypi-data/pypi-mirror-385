#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

import os
import random

import unittest
from sm3utils import sm3

class TestSm3(unittest.TestCase):


    def test01(self):
        gen = sm3()
        gen.update(b'abc')
        assert gen.hexdigest() == '66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0'
        assert gen.hexdigest() == '66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0'

    def test02(self):
        gen = sm3()
        gen.update(b'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd')
        assert gen.hexdigest() == 'debe9ff92275b8a138604889c18e5a4d6fdb70e5387e5765293dcba39c0c5732'
        assert gen.hexdigest() == 'debe9ff92275b8a138604889c18e5a4d6fdb70e5387e5765293dcba39c0c5732'

    def test03(self):
        gen = sm3()
        gen.update(b'a')
        gen.update(b'b')
        gen.update(b'c')
        assert gen.hexdigest() == '66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0'
        assert gen.hexdigest() == '66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0'
    
    def test04(self):
        gen = sm3()
        gen.update(b'abcdabcdabcdab')
        gen.update(b'cdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd')
        assert gen.hexdigest() == 'debe9ff92275b8a138604889c18e5a4d6fdb70e5387e5765293dcba39c0c5732'
        assert gen.hexdigest() == 'debe9ff92275b8a138604889c18e5a4d6fdb70e5387e5765293dcba39c0c5732'

    def test05(self):
        gen1 = sm3()
        gen1.update(b'abcdabcdabcdab')
        gen2 = gen1.copy()
        gen2.update(b'cdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd')
        assert gen2.hexdigest() == 'debe9ff92275b8a138604889c18e5a4d6fdb70e5387e5765293dcba39c0c5732'

    def test06(self):
        for _ in range(4096):
            length = random.randint(0, 1024)
            data = os.urandom(length)
            gen = sm3(data)
            v1 = gen.hexdigest()
            v2 = gen.hexdigest()
            assert v1 == v2

    def test07(self):
        g1 = sm3()
        g1.update(b'a')
        g2 = g1.copy()
        g2.update(b'b')
        g2.update(b'c')
        assert g2.hexdigest() == "66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0"
        assert g1.hexdigest() != "66c7f0f462eeedd9d1f2d46bdc10e4e24167c4875cf2f7a2297da02b8f4ba8e0"

    def test08(self):
        g1 = sm3()
        assert g1.block_size == 64
        assert g1.digest_size == 32
