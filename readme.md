# Proxy Checker

This Python script checks a list of proxies from a CSV file, determines their working status, measures their latency and speed, and sorts them into different output files. It also attempts to identify the proxy type (HTTP, HTTPS, SOCKS).

## Features

* **CSV Input:** Reads proxies from a CSV file, supporting both single-column (ip:port) and multi-column (ip/host, port) formats.
* **Threaded Checking:** Checks proxies concurrently using threads for faster processing.
* **Latency and Speed Measurement:** Calculates and records the latency and speed of working proxies.
* **Proxy Type Detection:** Attempts to identify the proxy type (HTTP, HTTPS, SOCKS) based on port number and network analysis.
* **Sorting and Saving:** Sorts working proxies by latency and speed and saves them into separate text files.
* **Working Proxy Output:** Saves all working proxies, along with their detected types, into a single file.
* **Robust Error Handling:** Handles various potential errors during proxy checking.

## Requirements

* Python 3.x
* `requests` library: `pip install requests`

## Usage

1.  **Create a CSV file:**
    * Create a CSV file (e.g., `proxies.csv`) containing your proxy list.
    * The CSV file can have one proxy per line (in the format `ip:port`), or it can have separate "ip" (or "host") and "port" columns.
    * Example single column format:
    ```csv
    1.2.3.4:8080
    5.6.7.8:3128
    ```
    * Example multi column format:
    ```csv
    ip,port
    1.2.3.4,8080
    5.6.7.8,3128
    ```

2.  **Run the script:**
    * Save the Python code as a `.py` file (e.g., `proxy_checker.py`).
    * Open your terminal and navigate to the directory where you saved the file.
    * Run the script using the following command:

    ```bash
    python proxy_checker.py
    ```

    * To use a different csv file name, run.
    ```bash
    python proxy_checker.py your_proxy_list.csv
    ```

3.  **View the results:**
    * The script will generate the following output files:
        * `working_proxies_latency.txt`: Working proxies sorted by latency (fastest first).
        * `working_proxies_speed.txt`: Working proxies sorted by speed (highest first).
        * `working_proxies_working.txt`: All working proxies with their detected types.
    * Each line in the output files will contain the proxy address and its type (e.g., `1.2.3.4:8080 (HTTP)`).

## Example CSV

```csv
ip,port
192.168.1.1,8080
10.0.0.1,3128
203.0.113.1,1080
