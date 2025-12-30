import requests
import hashlib
import time
import sys

def getchecksum():
    md5_hash = hashlib.md5()
    try:
        md5_hash.update(b"test")
        digest = md5_hash.hexdigest()
        return digest
    except:
        return ""

class api:
    def __init__(self, name, ownerid, version, hash_to_check=None):
        self.name = name
        self.ownerid = ownerid
        self.version = version
        self.hash_to_check = hash_to_check
        self.sessionid = None

    def init(self):
        self.name = "CAR Manager Pro"
        
        token = self.ownerid
        token_md5 = hashlib.md5(token.encode()).hexdigest()
        
        print(f"\n--- Testing with token={token} ---")
        
        # Test 1: token_hash parameter
        print("1. Parameter 'token_hash'")
        self.run_test({"token": token, "token_hash": token_md5})

        # Test 2: tokenhash parameter
        print("2. Parameter 'tokenhash'")
        self.run_test({"token": token, "tokenhash": token_md5})

        # Test 3: hash parameter (already tested, but confirming)
        print("3. Parameter 'hash'")
        self.run_test({"token": token, "hash": token_md5})

    def run_test(self, extra_params, url="https://keyauth.win/api/1.3/"):
        try:
            init_iv = hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
            
            data = {
                "type": "init",
                "ver": self.version,
                "name": self.name,
                "ownerid": self.ownerid,
                "init_iv": init_iv,
                # Note: We are overriding 'hash' in extra_params for Test 3
                "hash": self.hash_to_check 
            }
            data.update(extra_params)
            
            headers = {"User-Agent": "KeyAuth"}
            response = requests.post(url, data=data, headers=headers)
            print(f"Response: {response.text}")
            
        except Exception as e:
            print(f"Error: {e}")

# Test parameters
KA_NAME = "CAR Manager Pro"
KA_OWNERID = "sMVLc5nAqD"
KA_VERSION = "1.0"

app = api(KA_NAME, KA_OWNERID, KA_VERSION, getchecksum())
app.init()
