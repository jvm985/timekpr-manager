import paramiko
import os

class SSHManager:
    def __init__(self, username="joachim", key_path="~/.ssh/id_rsa"):
        self.username = username
        self.key_path = os.path.expanduser(key_path)
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self, host):
        """Verbinding maken met een host via SSH met sleutels."""
        try:
            self.client.connect(
                hostname=host,
                username=self.username,
                key_filename=self.key_path,
                timeout=5,
                allow_agent=True,
                look_for_keys=True
            )
            return True
        except Exception as e:
            print(f"Fout bij verbinden met {host}: {str(e)}")
            return False

    def execute_command(self, command):
        """Voert een commando uit op de verbonden host en geeft de output terug."""
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            return out, err
        except Exception as e:
            return "", f"Executiefout: {str(e)}"

    def get_users(self):
        """Haalt de lijst van gebruikers op via timekpra. Probeert sudo indien nodig."""
        # Eerst proberen zonder sudo
        out, err = self.execute_command("timekpra --getuserlist")
        
        # Als dat faalt of 'geen toegang' geeft, probeer met sudo
        if not out or "geen toegang" in out.lower() or "not authorized" in out.lower():
            out, err = self.execute_command("sudo timekpra --getuserlist")
        
        users = []
        if out:
            # Soms staat er 'X gebruikers' op de eerste regel, of andere info
            for line in out.split('\n'):
                u = line.strip()
                # Filter: Geen info-regels, geen lege regels, geen regels met spaties
                if u and " " not in u and not u.endswith("gebruikers") and not u.startswith("#") and not u.startswith("Opdracht"):
                    users.append(u)
        return users

    def get_user_limits(self, user):
        """Haalt de huidige tijdslimieten op voor een gebruiker. Probeert sudo indien nodig."""
        # Probeer eerst zonder sudo
        out, err = self.execute_command(f"timekpra --getuserinfo '{user}'")
        
        # Fallback naar sudo bij fouten
        if not out or "geen toegang" in out.lower():
            out, err = self.execute_command(f"sudo timekpra --getuserinfo '{user}'")
            
        limits = [0] * 7
        if out:
            for line in out.split('\n'):
                if line.startswith("LIMITS_PER_WEEKDAYS:"):
                    parts = line.split(":")[1].strip().split(";")
                    if len(parts) >= 7:
                        limits = [int(p) for p in parts[:7]]
                    break
        return limits

    def get_user_usage(self, user):
        """Haalt het actuele verbruik en de resterende tijd van vandaag op."""
        out, err = self.execute_command(f"timekpra --getuserinfo '{user}'")
        if not out or "geen toegang" in out.lower():
            out, err = self.execute_command(f"sudo timekpra --getuserinfo '{user}'")
            
        usage = {"spent": 0, "left": 0}
        if out:
            for line in out.split('\n'):
                if line.startswith("TIME_SPENT_DAY:"):
                    usage["spent"] = int(line.split(":")[1].strip())
                elif line.startswith("TIME_LEFT_DAY:"):
                    usage["left"] = int(line.split(":")[1].strip())
        return usage

    def set_limits(self, user, limits_list):
        """Stelt de tijdslimieten in voor alle 7 dagen (Ma-Zo) via sudo."""
        limits_str = ";".join(map(str, limits_list))
        # Voor schrijven is sudo ALTIJD nodig
        cmd = f"sudo timekpra --settimelimits '{user}' '{limits_str}'"
        out, err = self.execute_command(cmd)
        return out if not err else err

    def close(self):
        if self.client:
            self.client.close()
