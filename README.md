# TimeKpr Network Manager

Een grafische Linux-applicatie om [TimeKpr-nExT](https://mjasnik.gitlab.io/timekpr-next/) op meerdere apparaten in je netwerk te beheren via SSH.

## Functionaliteiten
- **Netwerk Scanner:** Vindt automatisch alle Linux-apparaten met SSH in je netwerk.
- **Real-time Monitoring:** Zie direct hoeveel tijd een gebruiker vandaag al heeft verbruikt.
- **Weekbeheer:** Stel eenvoudig tijdslimieten in voor elke dag van de week (uren en minuten).
- **SSH-Integratie:** Beheer alles veilig via SSH-sleutels, zonder wachtwoorden te typen.

## Vereisten

### Op de Manager PC (waarop je deze app draait):
- Python 3
- PyQt6, Paramiko, Psutil (`pip install PyQt6 paramiko psutil`)
- `nmap` (voor de netwerkscanner)

### Op de doeltoestellen (die je wilt beheren):
1. **TimeKpr-nExT** geïnstalleerd (`sudo apt install timekpr-next`).
2. **SSH-server** actief.
3. **SSH-sleutel** van de manager pc toegevoegd (`ssh-copy-id gebruiker@doel-ip`).
4. **Passwordless sudo** voor timekpra:
   ```bash
   echo "$USER ALL=(ALL) NOPASSWD: /usr/bin/timekpra" | sudo tee /etc/sudoers.d/timekpr
   ```

## Installatie
1. Clone deze repository:
   ```bash
   git clone https://github.com/jouwgebruikersnaam/timekpr-network-manager.git
   cd timekpr-network-manager
   ```
2. Start de applicatie:
   ```bash
   python3 gui.py
   ```

## Licentie
MIT
