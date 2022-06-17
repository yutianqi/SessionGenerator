import re
import os
import sys
import base64

import configparser

from getpass import getpass
from Crypto.Hash import SHA512
from Crypto.Cipher import AES, DES3


'''
s1_10.44.208.82 
(ossuser)
= 
#109
#0
  %10.44.208.82
  %22
  %ossuser
  %
  %-1
  %-1
  %
  %
  %
  %
  %0
  %0
  %0
  %
  %
  %-1
  %0
  %0
  %0
  %
  %1080
  %
  %0
  %0
  %1
#MobaFont
  %10
  %0
  %0
  %-1
  %15
  %236,236,236
  %30,30,30
  %180,180,192
  %0
  %-1
  %0
  %
  %xterm
  %-1
  %-1
  %_Std_Colors_0_
  %80
  %24
  %0
  %1
  %-1
  %<custom macro>
  %0:0:0:WAITFOREQUAL[ossuser@osssvr ~]$__PIPE__12:2:0:ssh ossadm@10.44.208.81__PIPE__258:13:18612225:RETURN__PIPE__0:0:0:WAITFOREQUALpassword__DBLDOT____PIPE__12:2:0:Changeme_123__PIPE__258:13:18612225:RETURN__PIPE__
  %0
  %0
  %-1
#0
# 
#-1


WAITFOREQUAL
[ossuser@osssvr ~]$
__PIPE__12:2:0:
ssh ossadm@10.44.208.82
__PIPE__258:13:18612225:
RETURN__PIPE__0:0:0:
WAITFOREQUAL
password__DBLDOT__
__PIPE__12:2:0:
Changeme_123
__PIPE__258:13:18612225:
RETURN
__PIPE__

'''
class Crypt():
    def __init__(self, master_password: str):
        self.key = SHA512.new(master_password.encode("utf-8")).digest()[0:32]

    def decrypt(self, ciphertext: str) -> bytes:
        iv = AES.new(key=self.key, mode=AES.MODE_ECB).encrypt(b'\x00' * AES.block_size)
        cipher = AES.new(key=self.key, iv=iv, mode=AES.MODE_CFB, segment_size=8)
        return cipher.decrypt(base64.b64decode(ciphertext)).decode("utf-8")

    def encrypt(self, Plaintext: str) -> str:
        iv = AES.new(key = self.key, mode = AES.MODE_ECB).encrypt(b'\x00' * AES.block_size)
        cipher = AES.new(key = self.key, iv = iv, mode = AES.MODE_CFB, segment_size = 8)
        return base64.b64encode(cipher.encrypt(Plaintext.encode("utf-8"))).decode("utf-8")


class MobaXtermSessionGenerator():
    crypt = Crypt('Huawei@123')
    print(crypt.decrypt("DCD/yTUSUDkL34PH"))
    print(crypt.encrypt("Changeme_123"))


generator = MobaXtermSessionGenerator()





