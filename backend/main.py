import json
import time
from netmiko import (
    ConnectHandler,
    NetMikoAuthenticationException,
    NetMikoTimeoutException,
)
from concurrent.futures import ThreadPoolExecutor, as_completed


def print_execution_time(end_total) -> None:
    if end_total > 1:
        print(f"\nTotal script execution time: {end_total:.2f} s")
    else:
        end_total *= 1000
        print(f"\nTotal script execution time: {end_total:.2f} ms")


def get_stp_data(device, retries=3):
    print("\ndevice: ", device)
    spanning_tree_command = device.get("spanning_tree_command")

    # List of keys to eliminate from the device dictionary
    keys_to_eliminate = ["spanning_tree_command"]

    # Create a new dictionary excluding the keys to eliminate
    netmiko_device = {k: v for k, v in device.items() if k not in keys_to_eliminate}
    print("netmiko_device: ", netmiko_device)

    for attempt in range(retries):
        try:
            connection = ConnectHandler(**netmiko_device)
            if "secret" in netmiko_device:
                connection.enable()
            output = connection.send_command(spanning_tree_command)
            connection.disconnect()
            return netmiko_device["host"], output, None
        except NetMikoAuthenticationException as e:
            print(
                f"\nFailed to connect to {netmiko_device['host']}: Authentication failed."
            )
            return netmiko_device["host"], None, "auth"
        except NetMikoTimeoutException as e:
            print(
                f"\nFailed to connect to {netmiko_device['host']}: TCP connection to device failed."
            )
            return netmiko_device["host"], None, "timeout"
        except Exception as e:
            print(
                f"\nFailed to connect to {netmiko_device['host']} on attempt {attempt + 1}: {e}"
            )
            time.sleep(2)  # Wait a bit before retrying
    return netmiko_device["host"], None, "other"


def main():
    CREDENTIALS_FILE = "./device_credentials.json"
    try:
        with open(CREDENTIALS_FILE, "r") as file:
            devices = json.load(file)
    except FileNotFoundError:
        print(f"Error: The file {CREDENTIALS_FILE} was not found")
        return

    # Counters for connections
    successful_connections = 0
    failed_connections = 0
    auth_failures = 0
    timeout_failures = 0
    other_failures = 0

    # Use ThreadPoolExecutor to connect to multiple devices concurrently
    stp_data = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_device = {
            executor.submit(get_stp_data, device): device for device in devices
        }
        for future in as_completed(future_to_device):
            host, data, error_type = future.result()
            if data:
                stp_data[host] = data
                successful_connections += 1
            else:
                failed_connections += 1
                if error_type == "auth":
                    auth_failures += 1
                elif error_type == "timeout":
                    timeout_failures += 1
                else:
                    other_failures += 1

    # Print the collected STP data
    for host, data in stp_data.items():
        print(f"STP data for {host}:\n{data}\n")

    # Print summary of connections
    print(f"\nSummary of connections")
    total_devices = len(devices)
    print(f"\n{total_devices} devices found in {CREDENTIALS_FILE} file")
    print(f"--Successful connections: {successful_connections}")
    print(f"--Failed connections: {failed_connections}")
    print(f"  --Authentication failures: {auth_failures}")
    print(f"  --Timeout failures: {timeout_failures}")
    print(f"  --Other failures: {other_failures}")

    # Process the data further as needed


if __name__ == "__main__":
    start_total = time.time()
    main()
    end_total = time.time() - start_total

    print_execution_time(end_total)
