
import os
import base64
import shutil
import win32api
import win32security
from Crypto.Hash import SHA256
from Crypto.Cipher import ARC4

from win32api import GetComputerName, GetUserName
from win32security import LookupAccountName, ConvertSidToStringSid
from Crypto.Hash import SHA256
from Crypto.Cipher import ARC4

class CipherUtils():

    @staticmethod
    def encrypt(passwd):
        key = CipherUtils.getkey()
        tmp = SHA256.new(key.encode('ascii')).digest()
        r3 = passwd.encode('ascii')
        r1 = ARC4.new(tmp).encrypt(r3) + \
            SHA256.new(passwd.encode('ascii')).digest()
        r = base64.b64encode(r1).decode('ascii')
        return r

    @staticmethod
    def getkey():
        userName = win32api.GetUserName()
        computerName = win32api.GetComputerName()
        userSID = win32security.LookupAccountName(
            computerName, userName)[0]
        userSIDString = win32security.ConvertSidToStringSid(userSID)
        return userName + userSIDString

    @staticmethod
    def getkey1():
        return input("Please input key: ")

    @staticmethod
    def decrypt_string(a2):
        # a1 = GetUserName() + ConvertSidToStringSid(LookupAccountName(GetComputerName(), GetUserName())[0])
        print("UserName=" + GetUserName())
        print("ComputerName=" + GetComputerName())
        print("AccountName=" + str(LookupAccountName(GetComputerName(), GetUserName())[0]))
        print("Sid=" + ConvertSidToStringSid(LookupAccountName(GetComputerName(), GetUserName())[0]))
        tmp = GetUserName()[::-1] + ConvertSidToStringSid(LookupAccountName(GetComputerName(), GetUserName())[0])
        a1 = tmp[::-1]
        print(a1)
        v1 = base64.b64decode(a2)
        v3 = ARC4.new(SHA256.new(a1.encode('ascii')).digest()).decrypt(v1[:len(v1) - 0x20])
        if SHA256.new(v3).digest() == v1[-32:]:
            return v3.decode('ascii')
        else:
            return "时间表"

if __name__ == "__main__":
    print(CipherUtils.encrypt("12345"))
    print(CipherUtils.decrypt_string("9Fxx3NosxpWtovfzh2EEUFU1nnjT8a+mkBPlaNlPWrHYpWgS/3Ya3sLwAbw4P5wFajfEeA=="))