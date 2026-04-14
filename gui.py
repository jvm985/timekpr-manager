import sys
import json
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QLabel, QPushButton, 
                             QSpinBox, QMessageBox, QGroupBox, QLineEdit, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from scanner import NetworkScanner
from ssh_manager import SSHManager

# Standaard Linux locatie voor configbestanden (~/.config/)
CONFIG_DIR = os.path.expanduser("~/.config/timekpr-network-manager")
CONFIG_FILE = os.path.join(CONFIG_DIR, "devices.json")

class ScanThread(QThread):
    device_found = pyqtSignal(dict)
    finished = pyqtSignal()

    def run(self):
        scanner = NetworkScanner()
        for device in scanner.scan_for_ssh_live():
            self.device_found.emit(device)
        self.finished.emit()

class TimeKprManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TimeKpr Network Manager")
        self.setGeometry(100, 100, 1000, 700)
        
        # Zorg dat de configmap bestaat
        os.makedirs(CONFIG_DIR, exist_ok=True)
        
        self.devices = self.load_devices()
        self.selected_device = None
        self.selected_user = None
        self.ssh_manager = None
        self.hour_inputs = []
        self.minute_inputs = []
        
        self.spinner_timer = QTimer()
        self.spinner_timer.timeout.connect(self.update_spinner_text)
        self.spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spinner_idx = 0
        
        self.usage_timer = QTimer()
        self.usage_timer.timeout.connect(self.refresh_usage_only)
        
        self.init_ui()
        self.check_dependencies()
        self.refresh_device_list()

    def check_dependencies(self):
        """Controleert of alle nodige programma's op het systeem staan."""
        deps = ["nmap", "ssh"]
        missing = []
        for dep in deps:
            if subprocess.run(["which", dep], capture_output=True).returncode != 0:
                missing.append(dep)
        if missing:
            QMessageBox.critical(self, "Ontbrekende tools", 
                                f"Installeer de volgende programma's om deze app te gebruiken: {', '.join(missing)}")

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # --- Linkerkant ---
        device_layout = QVBoxLayout()
        add_layout = QHBoxLayout()
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("IP (bijv. 192.168.0.3)")
        self.add_btn = QPushButton("Voeg toe")
        self.add_btn.clicked.connect(self.add_manual_device)
        add_layout.addWidget(self.ip_input)
        add_layout.addWidget(self.add_btn)
        device_layout.addLayout(add_layout)

        self.device_list = QListWidget()
        self.device_list.itemClicked.connect(self.device_selected)
        device_layout.addWidget(QLabel("Apparaten op netwerk:"))
        device_layout.addWidget(self.device_list)
        
        btn_layout = QHBoxLayout()
        self.remove_btn = QPushButton("Wissen")
        self.remove_btn.clicked.connect(self.remove_device)
        self.rescan_btn = QPushButton("Scan Netwerk")
        self.rescan_btn.clicked.connect(self.scan_network)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.rescan_btn)
        device_layout.addLayout(btn_layout)
        
        # --- Midden ---
        user_layout = QVBoxLayout()
        self.user_list = QListWidget()
        self.user_list.itemClicked.connect(self.user_selected)
        user_layout.addWidget(QLabel("Gebruikers:"))
        user_layout.addWidget(self.user_list)

        # --- Rechterkant ---
        self.settings_group = QGroupBox("Weekoverzicht Limieten")
        settings_main_layout = QVBoxLayout()
        
        self.status_label = QLabel("Selecteer een gebruiker...")
        self.status_label.setStyleSheet("font-weight: bold; color: blue; margin-bottom: 5px;")
        settings_main_layout.addWidget(self.status_label)
        
        self.usage_label = QLabel("")
        self.usage_label.setStyleSheet("color: #555; margin-bottom: 10px; font-style: italic;")
        settings_main_layout.addWidget(self.usage_label)

        header_row = QHBoxLayout()
        header_row.addWidget(QLabel("Dag"), 1)
        header_row.addWidget(QLabel("Uren"), 1)
        header_row.addWidget(QLabel("Minuten"), 1)
        header_row.addStretch(1)
        settings_main_layout.addLayout(header_row)

        days = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]
        for day in days:
            day_row = QHBoxLayout()
            label = QLabel(f"{day}:")
            hour_spin = QSpinBox()
            hour_spin.setRange(0, 24)
            hour_spin.setFixedWidth(70)
            min_spin = QSpinBox()
            min_spin.setRange(0, 59)
            min_spin.setFixedWidth(70)
            day_row.addWidget(label, 1)
            day_row.addWidget(hour_spin, 1)
            day_row.addWidget(min_spin, 1)
            day_row.addStretch(1)
            settings_main_layout.addLayout(day_row)
            self.hour_inputs.append(hour_spin)
            self.minute_inputs.append(min_spin)

        settings_main_layout.addSpacing(20)
        self.save_all_btn = QPushButton("Sla alles op via SSH")
        self.save_all_btn.setFixedHeight(45)
        self.save_all_btn.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold;")
        self.save_all_btn.clicked.connect(self.save_all_limits)
        settings_main_layout.addWidget(self.save_all_btn)
        settings_main_layout.addStretch()
        
        self.settings_group.setLayout(settings_main_layout)
        self.settings_group.setEnabled(False)

        layout.addLayout(device_layout, 1)
        layout.addLayout(user_layout, 1)
        layout.addWidget(self.settings_group, 2)

    def load_devices(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f: return json.load(f)
            except: return []
        return []

    def save_devices(self):
        with open(CONFIG_FILE, 'w') as f: json.dump(self.devices, f)

    def refresh_device_list(self):
        self.device_list.clear()
        for dev in self.devices:
            self.device_list.addItem(f"{dev.get('hostname', dev['ip'])} ({dev['ip']})")

    def add_manual_device(self):
        ip = self.ip_input.text().strip()
        if ip and not any(d['ip'] == ip for d in self.devices):
            self.devices.append({'ip': ip, 'hostname': ip})
            self.save_devices()
            self.refresh_device_list()
            self.ip_input.clear()

    def remove_device(self):
        idx = self.device_list.currentRow()
        if idx >= 0:
            del self.devices[idx]
            self.save_devices()
            self.refresh_device_list()
            self.user_list.clear()
            self.settings_group.setEnabled(False)
            self.usage_timer.stop()

    def scan_network(self):
        self.rescan_btn.setEnabled(False)
        self.spinner_timer.start(100)
        self.scan_thread = ScanThread()
        self.scan_thread.device_found.connect(self.on_device_found)
        self.scan_thread.finished.connect(self.on_scan_finished)
        self.scan_thread.start()

    def update_spinner_text(self):
        char = self.spinner_frames[self.spinner_idx % len(self.spinner_frames)]
        self.rescan_btn.setText(f"{char} Zoeken...")
        self.spinner_idx += 1

    def on_device_found(self, device):
        existing_ips = {d['ip'] for d in self.devices}
        if device['ip'] not in existing_ips:
            self.devices.append(device)
            self.save_devices()
            self.refresh_device_list()

    def on_scan_finished(self):
        self.spinner_timer.stop()
        self.rescan_btn.setEnabled(True)
        self.rescan_btn.setText("Scan Netwerk")

    def device_selected(self, item):
        idx = self.device_list.currentRow()
        if idx < 0: return
        self.selected_device = self.devices[idx]
        self.usage_timer.stop()
        
        if self.ssh_manager: self.ssh_manager.close()
        self.ssh_manager = SSHManager()
        if self.ssh_manager.connect(self.selected_device['ip']):
            users = self.ssh_manager.get_users()
            self.user_list.clear()
            for user in users: self.user_list.addItem(user)
        else:
            QMessageBox.critical(self, "Verbindingsfout", "Geen SSH-verbinding mogelijk. Controleer sleutels.")

    def user_selected(self, item):
        self.selected_user = item.text()
        self.settings_group.setEnabled(True)
        self.status_label.setText(f"Gebruiker: {self.selected_user}")
        self.refresh_usage_only()
        self.usage_timer.start(30000)
        
        limits_secs = self.ssh_manager.get_user_limits(self.selected_user)
        for i, total_sec in enumerate(limits_secs):
            if i < len(self.hour_inputs):
                self.hour_inputs[i].setValue(total_sec // 3600)
                self.minute_inputs[i].setValue((total_sec % 3600) // 60)

    def refresh_usage_only(self):
        if not self.selected_user or not self.ssh_manager: return
        try:
            usage = self.ssh_manager.get_user_usage(self.selected_user)
            self.usage_label.setText(f"Vandaag verbruikt: {usage['spent'] // 3600}u {(usage['spent'] % 3600) // 60}m  |  Resterend: {usage['left'] // 3600}u {(usage['left'] % 3600) // 60}m")
        except:
            self.usage_label.setText("Verbinding verbroken...")

    def save_all_limits(self):
        new_limits = [(self.hour_inputs[i].value() * 3600) + (self.minute_inputs[i].value() * 60) for i in range(7)]
        res = self.ssh_manager.set_limits(self.selected_user, new_limits)
        QMessageBox.information(self, "Resultaat", f"Beperkingen zijn succesvol bijgewerkt via SSH.")
        self.refresh_usage_only()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimeKprManagerApp()
    window.show()
    sys.exit(app.exec())
