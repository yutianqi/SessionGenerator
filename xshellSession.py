#/usr/bin/python
# *_* coding utf-8 *_*

import os
import stat
import sys
import base64
import shutil
import win32api
import win32security
import xlrd
import fileinput
from Crypto.Cipher import ARC4
from Crypto.Hash import SHA256
from optparse import OptionParser

if os.name is 'nt':
    delimiter = '\\'
elif os.name is 'posix':
    delimiter = '/'

def opts():
    "the options"
    parser = OptionParser()
    parser.add_option("-f", dest="file", help="the excel file hava message default ./message.xls")
    parser.add_option("-t", dest="template", help="the xshell session template file default ./template.xsh")
    parser.add_option("-s", dest="sheet", help="the message.xls sheet default is 1")
    options, args = parser.parse_args()
    if not options.file:
        inputfile = os.getcwd() + delimiter + 'message.xls'
    else:
        inputfile = options.file
        if not os.path.isfile(inputfile):
            print "your input file:%s not exist" %inputfile; sys.exit(1)
    if not options.template:
        template = os.getcwd() + delimiter + 'template.xsh'
    else:
        template = options.template
        if not os.path.isfile(template):
            print "you template file:%s not exist" %template; sys.exit(1)
    if not options.sheet:
        sheetnum = 0
    else:
        sheetnum = options.sheet - 1
    return inputfile, template, sheetnum

def readfile(messagefilename, sheetnum):
    "return list of the file rows message"
    message = []
    data = xlrd.open_workbook(messagefilename)
    xlstable = data.sheet_by_index(sheetnum)
    rows = xlstable.nrows
    message.append(rows)
    for row in range(1, rows):
        rowdatas = xlstable.row_values(row)
        if not (len(rowdatas)-1) % 3 == 0:
            print "have err at message.xls row: %d" %row; sys.exit(1)
        message.append({row: rowdatas})
    return message

def processmess(messagefilename,template, sheetnum):
    "process readfile message"
    messlist = readfile(messagefilename, sheetnum)
    rows = messlist[0]
    for row in range(1, rows):
        createfile(messlist[row][row], template)

def createfile(rowlist, template, port=22):
    "create session file by template file"
    if len(rowlist)-3 > 0:
        num = (len(rowlist)-3) / 3
    dir = os.getcwd() + delimiter + 'session'
    dest = dir + delimiter + rowlist[-1] + '.xsh'
    if not os.path.isdir(dir):
        os.makedirs(dir)
    shutil.copyfile(template, dest)
    os.chmod(dest, stat.S_IRWXU)
    for line in fileinput.input(dest, inplace=1):
        if line.startswith("Port="):
            print 'Port=%d'.strip() %port
        elif line.startswith("Host="):
            print 'Host=%s'.strip() %rowlist[2]
        elif line.startswith('Password='):
            print 'Password=%s'.strip() %encrypt(rowlist[1])
        elif line.startswith('UserName='):
            print 'UserName=%s'.strip() %rowlist[0]
        elif line.startswith('[CONNECTION:AUTHENTICATION]'):
            expects = writestring(num, rowlist[3:])
            if expects:
                print (line.strip() + '\n' + expects).strip()
            else:
                print line.strip()
        else:
            print line.strip()

def writestring(num, rlist):
    "return what you want to write"
    wstring = ''
    for i in range(num):
        sshstr = 'ssh %s@%s' %(rlist.pop(0), rlist.pop(1))
        sshstr = encrypt(sshstr)
        wstring += '''ExpectSend_Expect_%s=login\nExpectSend_Send_%s=%s\nExpectSend_Hide_%s=1\nExpectSend_Expect_%s=password\nExpectSend_Send_%s=%s\nExpectSend_Hide_%s=1\n'''\
                  %(i, i, sshstr, i, i+1, i+1, encrypt(rlist.pop(0)), i+1)
    return wstring.strip('\n')

def getkey():
    "return winsystem key only by win system"
    CurrentUserName = win32api.GetUserName()
    CurrentComputerName = win32api.GetComputerName()
    CurrentUserSID = win32security.LookupAccountName(CurrentComputerName, CurrentUserName)[0]
    CurrentuserSIDString = win32security.ConvertSidToStringSid(CurrentUserSID)
    return CurrentUserName + CurrentuserSIDString

def encrypt(passwd, key=None):
    "to encrypt passwd by key"
    if not key:
        key = getkey()
    cipher_key = SHA256.new(key).digest()
    cipher = ARC4.new(cipher_key)
    encrypt_passwd = cipher.encrypt(str(passwd))
    tmp_passwd = SHA256.new(passwd).digest()
    result =(encrypt_passwd + tmp_passwd).encode('base64').strip('\n')
    return result

def main():
    inputfile, template, sheetnum = opts()
    processmess(inputfile,template, sheetnum)

if __name__ == '__main__':
    main()
