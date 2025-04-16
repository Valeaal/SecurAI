import time
import socket
import nmap

running = False  # Variable global de control

def get_local_ip():
    """Obtiene la IP local de la máquina en la red"""
    try:
        # Crear un socket temporal para obtener la IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Conectar a un servidor externo para descubrir la IP
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error al obtener IP local: {e}")
        return "127.0.0.1"  # Fallback a localhost si falla

def attack(target_ip=None, port_range="1-100", scan_type="-sT"):
    """
    Simula un ataque de reconocimiento usando un escaneo TCP SYN de Nmap.
    
    Args:
        target_ip (str): Dirección IP objetivo (por defecto: IP local si None)
        port_range (str): Rango de puertos a escanear (por defecto: 1-100)
        scan_type (str): Tipo de escaneo de Nmap (por defecto: -sS para TCP SYN)
    """
    global running
    
    if target_ip is None:
        target_ip = get_local_ip()  # Usa la IP local si no se especifica
    
    try:
        print(f"Iniciando ataque de reconocimiento en {target_ip}, puertos {port_range}")
        running = True
        
        nm = nmap.PortScanner()
        
        while True:
            while running:
                # Realiza el escaneo
                nm.scan(target_ip, port_range, arguments=scan_type)
                
                # Imprime los resultados del escaneo (opcional)
                for host in nm.all_hosts():
                    print(f"Host: {host}")
                    for proto in nm[host].all_protocols():
                        print(f"Protocolo: {proto}")
                        ports = nm[host][proto].keys()
                        for port in ports:
                            state = nm[host][proto][port]['state']
                            print(f"Puerto: {port}\tEstado: {state}")
                
                # Pausa breve entre ciclos de escaneo
                time.sleep(1)
            
            time.sleep(1)  # Espera mientras está pausado
        
    except Exception as e:
        print(f"Error durante el ataque: {e}")
