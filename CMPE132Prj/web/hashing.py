import hashlib
import os

def makeSalt():
    return os.urandom(8).hex()

def hashSalt(password, salt):
    w = ord(password[0])
    x = ord(password[1]) * 10
    y = ord(password[2]) * pow(10, 2)
    z = ord(password[3]) * pow(10, 3)
    total = w + x + y + z
    hash = password + str(total) + salt
    return hash

def hashFun(password):
    salt = makeSalt()
    hash = hashSalt(password, salt)
    return hash, salt

def verify(pSalt, pHash, input):
    return hashSalt(input, pSalt) == pHash