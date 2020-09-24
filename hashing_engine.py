#   Copyright 2020 Stanford University
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
from Crypto.Cipher import AES
import base64
import os

secret_key = os.environ['EMAILING_HASHING_KEY'] # create new & store somewhere safe

def encrypt(email):

    cipher = AES.new(secret_key,AES.MODE_ECB) # never use ECB in strong systems 
    encoded = base64.b64encode(cipher.encrypt(email.rjust(32)))

    return encoded

def decrypt(encoded):

    cipher = AES.new(secret_key,AES.MODE_ECB) # never use ECB in strong systems 
    decoded_email = cipher.decrypt(base64.b64decode(encoded)).strip()
    return decoded_email.decode("utf-8") 

