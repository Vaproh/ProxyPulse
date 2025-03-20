import csv
import json
import requests
import time
import threading
from queue import Queue
import socket
import os
from datetime import datetime
import argparse

# Color codes for terminal output
COLORS = {
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "MAGENTA": "\033[95m",
    "CYAN": "\033[96m",
    "WHITE": "\033[97m",
    "BOLD": "\033[1m",
    "RESET": "\033[0m",
}


def colored(text, color):
    """Return colored text using ANSI escape codes."""
    return f"{COLORS[color]}{text}{COLORS['RESET']}"


def get_country(ip):
    """Gets the country of an IP address using ip-api.com."""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("country", "Unknown")
    except (requests.exceptions.RequestException, KeyError):
        return "Unknown"


def check_proxy(proxy, results, timeout=5, proxy_data=None):
    """Checks if a proxy is working and returns its metrics."""
    try:
        ip, port = proxy.split(":")
        start_time = time.time()

        # Use existing data if available
        if proxy_data and all(
            key in proxy_data for key in ["latency", "speed", "type", "country"]
        ):
            results.put(
                (
                    True,
                    proxy,
                    proxy_data["latency"],
                    proxy_data["speed"],
                    proxy_data["type"],
                    proxy_data["country"],
                )
            )
            status = colored("WORKING (CACHED)", "GREEN")
            details = (
                f"Latency: {colored(f'{proxy_data["latency"]:.4f}s', 'CYAN')}, "
                f"Speed: {colored(f'{proxy_data["speed"]:.2f} B/s', 'MAGENTA')}, "
                f"Type: {colored(proxy_data['type'], 'YELLOW')}, "
                f"Country: {colored(proxy_data['country'], 'BLUE')}"
            )
            print(f"{colored(proxy, 'BOLD')} - {status} | {details}")
            return

        # Test proxy with a HEAD request to reduce bandwidth
        response = requests.head(
            "http://httpbin.org/ip",
            proxies={"http": proxy, "https": proxy},
            timeout=timeout,
        )
        response.raise_for_status()

        latency = time.time() - start_time
        speed = len(response.content) / latency if latency > 0 else 0
        proxy_type = determine_proxy_type(proxy)
        country = get_country(ip)

        results.put((True, proxy, latency, speed, proxy_type, country))
        status = colored("WORKING", "GREEN")
        details = (
            f"Latency: {colored(f'{latency:.4f}s', 'CYAN')}, "
            f"Speed: {colored(f'{speed:.2f} B/s', 'MAGENTA')}, "
            f"Type: {colored(proxy_type, 'YELLOW')}, "
            f"Country: {colored(country, 'BLUE')}"
        )
        print(f"{colored(proxy, 'BOLD')} - {status} | {details}")

    except (Exception, OSError, socket.error) as e:
        results.put((False, proxy, 0, 0, "Unknown", "Unknown"))
        status = colored("FAILED", "RED")
        print(f"{colored(proxy, 'BOLD')} - {status} | {str(e)}")


def determine_proxy_type(proxy):
    """Determine proxy type with improved detection."""
    try:
        ip, port = proxy.split(":")
        port = int(port)

        # Common port-based detection
        if port == 1080:
            return "SOCKS5"
        elif port == 443:
            return "HTTPS"
        elif port in [80, 8080, 3128]:
            return "HTTP"

        # Protocol detection
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((ip, port))
                s.send(b"GET / HTTP/1.1\r\nHost: httpbin.org\r\n\r\n")
                if b"HTTP/1.1" in s.recv(1024):
                    return "HTTP"
        except:
            pass

        return "Unknown"

    except (ValueError, socket.error):
        return "Unknown"


def load_proxies_from_csv(filename):
    """Load proxies from CSV with improved error handling."""
    proxies = []
    try:
        with open(filename, "r") as f:
            reader = csv.reader(f)
            header = [col.lower() for col in next(reader, [])]

            if "ip" in header and "port" in header:
                ip_idx = header.index("ip")
                port_idx = header.index("port")
                for row in reader:
                    if len(row) > max(ip_idx, port_idx):
                        # Handle both ip:port and ip,port formats
                        if ":" in row[ip_idx]:  # ip:port format
                            proxy = row[ip_idx]
                        else:  # ip,port format
                            proxy = f"{row[ip_idx]}:{row[port_idx]}"

                        # Check for additional data
                        proxy_data = {}
                        if "latency" in header:
                            latency_idx = header.index("latency")
                            proxy_data["latency"] = float(row[latency_idx])
                        if "speed" in header:
                            speed_idx = header.index("speed")
                            proxy_data["speed"] = float(row[speed_idx])
                        if "type" in header:
                            type_idx = header.index("type")
                            proxy_data["type"] = row[type_idx]
                        if "country" in header:
                            country_idx = header.index("country")
                            proxy_data["country"] = row[country_idx]

                        proxies.append((proxy, proxy_data))
            else:
                f.seek(0)
                for row in reader:
                    if len(row) > 1:
                        # Handle both ip:port and ip,port formats
                        if ":" in row[0]:  # ip:port format
                            proxy = row[0]
                        else:  # ip,port format
                            proxy = f"{row[0]}:{row[1]}"
                        proxies.append((proxy, {}))
                    elif row:  # Handle single-column format
                        proxies.extend((p, {}) for p in row if ":" in p)

    except Exception as e:
        print(colored(f"Error loading CSV: {str(e)}", "RED"))
    return [(p, data) for p, data in proxies if validate_proxy_format(p)]


def load_proxies_from_json(filename):
    """Load proxies from JSON file."""
    proxies = []
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            if isinstance(data, dict):
                if "proxies" in data:
                    proxies = data["proxies"]
                elif "hosts" in data:
                    proxies = [f"{h['ip']}:{h['port']}" for h in data["hosts"]]
            elif isinstance(data, list):
                proxies = data

        formatted_proxies = []
        for proxy in proxies:
            if isinstance(proxy, str):
                if "," in proxy:  # ip,port format
                    ip, port = proxy.split(",")
                    formatted_proxies.append((f"{ip}:{port}", {}))
                else:  # ip:port format
                    formatted_proxies.append((proxy, {}))
            elif isinstance(proxy, dict):  # Handle {"ip": "x.x.x.x", "port": "xxxx"}
                proxy_data = {
                    "latency": proxy.get("latency", 0),
                    "speed": proxy.get("speed", 0),
                    "type": proxy.get("type", "Unknown"),
                    "country": proxy.get("country", "Unknown"),
                }
                formatted_proxies.append((f"{proxy['ip']}:{proxy['port']}", proxy_data))

        proxies = formatted_proxies

    except Exception as e:
        print(colored(f"Error loading JSON: {str(e)}", "RED"))
    return [(p, data) for p, data in proxies if validate_proxy_format(p)]


def load_proxies_from_txt(filename):
    """Load proxies from TXT file."""
    proxies = []
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    # Handle both ip:port and ip,port formats
                    if "," in line:  # ip,port format
                        ip, port = line.split(",")
                        proxies.append((f"{ip}:{port}", {}))
                    else:  # ip:port format
                        proxies.append((line, {}))
    except Exception as e:
        print(colored(f"Error loading TXT: {str(e)}", "RED"))
    return [(p, data) for p, data in proxies if validate_proxy_format(p)]


def validate_proxy_format(proxy):
    """Validate basic proxy format."""
    if ":" not in proxy:
        return False
    ip, port = proxy.split(":", 1)
    try:
        int(port)
        return True
    except ValueError:
        return False


def check_proxies_threaded(proxies, max_threads=20):
    """Check proxies with thread pool for better resource management."""
    results = Queue()
    threads = []

    # Create thread pool
    for proxy, proxy_data in proxies:
        while threading.active_count() > max_threads:
            time.sleep(0.1)
        thread = threading.Thread(
            target=check_proxy, args=(proxy, results, 5, proxy_data)
        )
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    return [results.get() for _ in range(results.qsize())]


def sort_and_save_proxies(
    checked_proxies, output_folder, sort_by=None, create_clean=False
):
    """Save results with enhanced organization, metadata, and working report."""
    working = [p for p in checked_proxies if p[0]]
    failed = [p for p in checked_proxies if not p[0]]

    if not working:
        print(colored("No working proxies found!", "RED"))
        return

    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_folder, f"results_{timestamp}")
    os.makedirs(output_path, exist_ok=True)

    # Calculate statistics
    total_tested = len(checked_proxies)
    success_rate = (len(working) / total_tested) * 100
    avg_latency = sum(p[2] for p in working) / len(working)
    avg_speed = sum(p[3] for p in working) / len(working)

    # Save detailed working report in CSV
    csv_report_path = os.path.join(output_path, "working_report.csv")
    with open(csv_report_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["Proxy", "Type", "Country", "Latency (s)", "Speed (B/s)", "Status"]
        )
        for proxy in working:
            writer.writerow(
                [
                    proxy[1],  # Proxy address
                    proxy[4],  # Type
                    proxy[5],  # Country
                    f"{proxy[2]:.4f}",  # Latency
                    f"{proxy[3]:.2f}",  # Speed
                    "WORKING",
                ]
            )
        for proxy in failed:
            writer.writerow([proxy[1], "N/A", "N/A", "N/A", "N/A", "FAILED"])

    # Save summary statistics
    summary_path = os.path.join(output_path, "summary.txt")
    with open(summary_path, "w") as f:
        f.write(f"=== Proxy Check Summary ===\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Total Tested: {total_tested}\n")
        f.write(f"Working Proxies: {len(working)}\n")
        f.write(f"Failed Proxies: {len(failed)}\n")
        f.write(f"Success Rate: {success_rate:.2f}%\n")
        f.write(f"Average Latency: {avg_latency:.4f}s\n")
        f.write(f"Average Speed: {avg_speed:.2f} B/s\n")

    # Save sorted proxies
    sorting_methods = {
        None: ("working_proxies.txt", lambda x: x[1]),
        "latency": ("latency_sorted.txt", lambda x: x[2]),
        "speed": ("speed_sorted.txt", lambda x: -x[3]),
    }

    for sort_type, (filename, key) in sorting_methods.items():
        if sort_by != sort_type and sort_type is not None:
            continue

        sorted_proxies = sorted(working, key=key)
        with open(os.path.join(output_path, filename), "w") as f:
            for proxy in sorted_proxies:
                f.write(f"{proxy[1]}\n")

    print(colored(f"\nResults saved to: {output_path}", "GREEN"))
    print(colored(f"Detailed report: {csv_report_path}", "CYAN"))
    print(colored(f"Summary stats: {summary_path}", "CYAN"))

def load_proxies_from_folder(folder_path):
    """Load proxies from multiple files within a folder."""
    proxies = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith('.csv'):
            proxies.extend(load_proxies_from_csv(file_path))
        elif filename.endswith('.json'):
            proxies.extend(load_proxies_from_json(file_path))
        elif filename.endswith('.txt'):
            proxies.extend(load_proxies_from_txt(file_path))
    return proxies

def main():
    parser = argparse.ArgumentParser(
        description="Advanced Proxy Checker with Multi-File Support",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--input", default="proxies",
        help="Input file or directory containing proxy files"
    )
    parser.add_argument(
        "--output", default="proxy_results",
        help="Output directory for results"
    )
    parser.add_argument(
        "--threads", type=int, default=20,
        help="Maximum concurrent threads"
    )
    parser.add_argument(
        "--sort", choices=["latency", "speed"],
        help="Sort working proxies by metric"
    )
    parser.add_argument(
        "--timeout", type=int, default=5,
        help="Timeout for proxy checks in seconds"
    )
    parser.add_argument(
        "--help", action="help", help="Show this help message and exit"
    )

    args = parser.parse_args()

    print("\n=== Proxy Checker ===")
    print(f"Loading proxies from {args.input}...")

    if os.path.isfile(args.input):
        if args.input.endswith('.csv'):
            proxies = load_proxies_from_csv(args.input)
        elif args.input.endswith('.json'):
            proxies = load_proxies_from_json(args.input)
        elif args.input.endswith('.txt'):
            proxies = load_proxies_from_txt(args.input)
        else:
            print("Unsupported file format!")
            return
    elif os.path.isdir(args.input):
        proxies = load_proxies_from_folder(args.input)
    else:
        print("Invalid input path!")
        return

    if not proxies:
        print("No valid proxies found!")
        return

    print(f"Loaded {len(proxies)} proxies")
    print(f"Starting checks with {args.threads} threads...\n")

    start_time = time.time()
    checked_proxies = check_proxies_threaded(proxies, args.threads)
    duration = time.time() - start_time

    print(f"\nCompleted checks in {duration:.2f} seconds")
    sort_and_save_proxies(checked_proxies, args.output, args.sort, True)

if __name__ == "__main__":
    main()

