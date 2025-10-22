#!/usr/bin/env python
# -*- coding: utf8 -*-

__all__ = [
    "sm3",
]

import binascii
import _sm3 as sm3core

class sm3(object):

    digest_size = 32
    block_size = 64

    def __init__(self, data=None):
        self.ctx = sm3core.pysm3_init()
        if data:
            self.update(data)
    
    def __del__(self):
        if self.ctx:
            sm3core.pysm3_free(self.ctx)
            self.ctx = None
    
    def update(self, data):
        sm3core.pysm3_update(self.ctx, data)
        return

    def digest(self):
        digest = sm3core.pysm3_final(self.ctx)
        return digest
    
    def hexdigest(self):
        digest = sm3core.pysm3_final(self.ctx)
        return binascii.hexlify(digest).decode()

    def copy(self):
        new_instance = sm3()
        sm3core.pysm3_copy(self.ctx, new_instance.ctx)
        return new_instance

