import subprocess
import socket
import psutil
import os

class NetworkScanner:
    def __init__(self):
        self.local_hostname = socket.gethostname()
        self.local_ips = self._get_all_local_ips()

    def _get_all_local_ips(self):
        ips = []
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ips.append(addr.address)
        return ips

    def get_gateway(self):
        """Probeert de standaard gateway (router) te vinden."""
        try:
            # Gebruik ip route om de default gateway te vinden
            result = subprocess.run(["ip", "route", "show", "default"], capture_output=True, text=True)
            if result.stdout:
                return result.stdout.split()[2]
        except:
            pass
        return "192.168.1.1" # Veilige fallback

    def get_local_subnet(self):
        """Haalt het subnet op van de actieve interface."""
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                    ip_parts = addr.address.split(".")
                    return f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
        return "192.168.1.0/24"

    def scan_for_ssh_live(self, subnet=None):
        """Scant het netwerk live met automatische detectie van omgeving."""
        if not subnet:
            subnet = self.get_local_subnet()
        
        gateway = self.get_gateway()
        
        # Geoptimaliseerd commando voor universeel gebruik
        cmd = [
            "nmap", "-p", "22", "--open", 
            "--dns-servers", gateway, 
            "-T4", "--min-rate", "1000", 
            subnet
        ]
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except FileNotFoundError:
            print("FOUT: nmap is niet geïnstalleerd.")
            return

        current_ip = None
        current_hostname = None
        
        for line in process.stdout:
            line = line.strip()
            if "Nmap scan report for" in line:
                parts = line.split()
                if len(parts) >= 6:
                    current_hostname = parts[4]
                    current_ip = parts[5].strip("()")
                else:
                    current_hostname = ""
                    current_ip = parts[4]
            
            elif "22/tcp open" in line and current_ip:
                if current_hostname == self.local_hostname and current_ip not in self.local_ips:
                    current_hostname = ""
                
                yield {
                    'ip': current_ip,
                    'hostname': current_hostname if current_hostname else current_ip,
                    'status': 'online'
                }
        process.wait()
