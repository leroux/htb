tcp scan
---
nmap -v -sC -sV -T5 <target>
nmap -v -sC -sV -T5 -p- <target>

rustscan -r 0-65535 -a <target>
rustscan -r 0-65535 -a <target> -- -A -sC


udp scan
---
nmap -v -sC -sV -T5 -sU <target>
nmap -v -sC -sV -T5 -sU -p- <target>
rustscan -r 0-65535 -a <target> --udp

subdomain enum
---
ffuf -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt -u http://FUZZ.codeparttwo.htb

upgrade to better shell
---
python3 -c 'import pty; pty.spawn("/bin/bash")'
ctrl-z
stty raw -echo; fg


payoad all the things
searchsploit

python3 -c 'import pty; pty.spawn("/bin/bash")'
