from Crypto.Cipher import AES
import base64
import os

msg_text = 'mypersonalmail@gmail.com'
secret_key = os.environ['EMAILING_HASHING_KEY'] # create new & store somewhere safe

def encrypt(email):

    cipher = AES.new(secret_key,AES.MODE_ECB) # never use ECB in strong systems 
    encoded = base64.b64encode(cipher.encrypt(email.rjust(32)))

    return encoded

def decrypt(encoded):

    cipher = AES.new(secret_key,AES.MODE_ECB) # never use ECB in strong systems 
    decoded_email = cipher.decrypt(base64.b64decode(encoded)).strip()
    return decoded_email


