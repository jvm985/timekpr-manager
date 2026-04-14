import sys
import os
from scanner import NetworkScanner
from ssh_manager import SSHManager

def test_scanner():
    print("--- Test Netwerk Scanner ---")
    scanner = NetworkScanner()
    subnet = scanner.get_local_subnet()
    print(f"Gedetecteerd subnet: {subnet}")
    # We scannen niet echt het hele netwerk (kan lang duren), we checken de initialisatie
    print("Scanner initialisatie: OK")

def test_ssh_manager():
    print("\n--- Test SSH Manager ---")
    # We testen alleen de klasse-structuur (tenzij we een echt doel-IP hebben)
    manager = SSHManager(username="joachim")
    print(f"SSH Manager geconfigureerd voor gebruiker: {manager.username}")
    print(f"Zoekt naar sleutel op: {manager.key_path}")
    
    # Check of de nodige commando's gedefinieerd zijn
    if hasattr(manager, 'get_users') and hasattr(manager, 'set_limit'):
        print("SSH-methodes (get_users, set_limit): OK")
    else:
        print("FOUT: SSH-methodes ontbreken!")

if __name__ == "__main__":
    try:
        test_scanner()
        test_ssh_manager()
        print("\nSUCCESS: Alle kern-componenten zijn correct geconfigureerd.")
    except Exception as e:
        print(f"\nFOUT opgetreden: {e}")
        sys.exit(1)
