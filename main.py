import csv
import requests
import time
import threading
from queue import Queue
import socket

def check_proxy(proxy, results, timeout=5):
    """Checks if a proxy is working and returns its latency, speed, and type."""
    try:
        start_time = time.time()
        response = requests.get("http://httpbin.org/ip", proxies={"http": proxy, "https": proxy}, timeout=timeout)
        end_time = time.time()
        latency = end_time - start_time
        speed = len(response.content) / latency if latency > 0 else 0

        # Attempt to determine proxy type
        proxy_type = determine_proxy_type(proxy)

        results.put((True, proxy, latency, speed, proxy_type))
    except (requests.exceptions.RequestException, OSError, ValueError, socket.error):
        results.put((False, proxy, 0, 0, "Unknown"))

def determine_proxy_type(proxy):
    """Attempts to determine the proxy type."""
    try:
        ip, port = proxy.split(":")
        port = int(port)

        # Basic port-based type guessing (not always accurate)
        if port == 1080:
            return "SOCKS"
        elif port == 443:
            return "HTTPS"
        elif port == 80 or 8080:
            return "HTTP"
        else:
          #more robust type detection
          s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          s.settimeout(1)
          s.connect((ip, port))
          s.send(b"GET / HTTP/1.1\r\nHost: httpbin.org\r\n\r\n")
          data = s.recv(1024)
          s.close()
          if b"HTTP/1.1" in data:
              return "HTTP"
          else:
              return "Unknown"

    except (ValueError, socket.error, TimeoutError):
        return "Unknown"

def load_proxies_from_csv(filename):
    """Loads proxies from a CSV file, handling IP and port columns."""
    proxies = []
    try:
        with open(filename, "r") as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader, None)  # Get the header row

            if header and ("ip" in [h.lower() for h in header] or "host" in [h.lower() for h in header]) and "port" in [h.lower() for h in header]:
                ip_index = [h.lower() for h in header].index("ip") if "ip" in [h.lower() for h in header] else [h.lower() for h in header].index("host")
                port_index = [h.lower() for h in header].index("port")
                for row in reader:
                    if len(row) > max(ip_index, port_index): #check if row has enough columns
                        ip = row[ip_index]
                        port = row[port_index]
                        proxies.append(f"{ip}:{port}")
            else:
                csvfile.seek(0) #reset file pointer if no ip/port header
                for row in csv.reader(csvfile):
                    if row:
                        proxies.extend(row)

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    return proxies

def check_proxies_threaded(proxies, num_threads=10):
    """Checks proxies in parallel using threads."""
    results = Queue()
    threads = []

    for proxy in proxies:
        thread = threading.Thread(target=check_proxy, args=(proxy, results))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    checked_proxies = []
    while not results.empty():
        checked_proxies.append(results.get())

    return checked_proxies

def sort_and_save_proxies(checked_proxies, output_prefix="working_proxies"):
    """Sorts and saves working proxies based on latency, speed, and type."""
    working_proxies = [proxy for working, proxy, latency, speed, proxy_type in checked_proxies if working]

    if not working_proxies:
        print("No working proxies found.")
        return

    # Sort by latency
    latency_sorted = sorted(working_proxies, key=lambda proxy: next((latency for working, p, latency, speed, proxy_type in checked_proxies if p == proxy), float('inf')))
    with open(f"{output_prefix}_latency.txt", "w") as f:
        for proxy in latency_sorted:
            proxy_type = next((proxy_type for working, p, latency, speed, proxy_type in checked_proxies if p == proxy), "Unknown")
            f.write(f"{proxy} ({proxy_type})\n")

    # Sort by speed
    speed_sorted = sorted(working_proxies, key=lambda proxy: next((speed for working, p, latency, speed, proxy_type in checked_proxies if p == proxy), 0), reverse=True)
    with open(f"{output_prefix}_speed.txt", "w") as f:
        for proxy in speed_sorted:
            proxy_type = next((proxy_type for working, p, latency, speed, proxy_type in checked_proxies if p == proxy), "Unknown")
            f.write(f"{proxy} ({proxy_type})\n")

    # Save all working proxies with type
    with open(f"{output_prefix}_working.txt", "w") as f:
        for proxy in working_proxies:
            proxy_type = next((proxy_type for working, p, latency, speed, proxy_type in checked_proxies if p == proxy), "Unknown")
            f.write(f"{proxy} ({proxy_type})\n")

def main(csv_file="proxies.csv"):
    """Main function to load, check, and sort proxies."""
    proxies = load_proxies_from_csv(csv_file)
    if not proxies:
        return

    print(f"Checking {len(proxies)} proxies...")
    checked_proxies = check_proxies_threaded(proxies)
    sort_and_save_proxies(checked_proxies)
    print("Proxy checking and sorting complete.")

if __name__ == "__main__":
    main()
