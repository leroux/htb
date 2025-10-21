app is running j2 code with js2py
use js2py exploit to run bash reverse shell
exfil sqlite db at instance/users.db via python http server
user password is in md5
brute force it

└─$ hashcat -m 0 marco.md5 /usr/share/wordlists/rockyou.txt -a 0 --show
649c9d65a206a75f5abe509fe128bce5:sweetangelbabylove

sudo -l shows i can run npbackup-cli

set npbackup.conf with pre-exec commands to start reverse shell for root
run with sudo npbackup-cli -c <config> --backup --force -v

get root
