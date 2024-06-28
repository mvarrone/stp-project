import json
import time
from netmiko import (
    ConnectHandler,
    NetMikoAuthenticationException,
    NetMikoTimeoutException,
)
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from pprint import pprint


def print_execution_time(end_total) -> None:
    if end_total > 1:
        print(f"\nTotal script execution time: {end_total:.2f} s")
    else:
        end_total *= 1000
        print(f"\nTotal script execution time: {end_total:.2f} ms")


def find_root_bridge(netmiko_device, data_raw, prompt):
    """We need to find the root bridge by OS"""
    operating_system = netmiko_device.get("device_type")
    host = netmiko_device.get("host")

    if operating_system == "cisco_ios":
        text_to_find = "This bridge is the root"
        if re.search(text_to_find, data_raw):
            print(
                f"\nRoot Bridge found. Detected in the output of {prompt} - {host} - {operating_system}\n"
            )
            root_bridge_data = {
                "prompt": prompt,
                "host": host,
                "operating_system": operating_system,
            }
            return root_bridge_data
    return None


def get_prompt(conn):
    prompt = conn.find_prompt()
    # print(f"{prompt = }")
    if not prompt:
        return "prompt not found"

    if prompt[-1] == "#":
        prompt = prompt[:-1]

    # print(f"{prompt = }")
    return prompt


def get_stp_data(device, retries=3):
    # print("\ndevice: ", device)
    spanning_tree_command = device.get("spanning_tree_command")
    cdp_neighbors_command = device.get("cdp_neighbors_command")

    # List of keys to eliminate from the device dictionary
    keys_to_eliminate = ["spanning_tree_command", "cdp_neighbors_command"]

    # Create a new dictionary excluding the keys to eliminate
    netmiko_device = {k: v for k, v in device.items() if k not in keys_to_eliminate}
    # print("\nnetmiko_device: ", netmiko_device)

    host = netmiko_device.get("host")
    port = netmiko_device.get("port")

    for attempt in range(retries):
        try:
            with ConnectHandler(**netmiko_device) as connection:
                if "secret" in netmiko_device:
                    connection.enable()

                # Get prompt
                prompt = get_prompt(connection)
                print(f"Prompt: {prompt}")

                # Capture raw output for STP
                data_raw = connection.send_command(
                    command_string=spanning_tree_command, use_textfsm=False
                )
                print(f"\ndata_raw for {host}:\n", data_raw)

                # Get parsed data with TextFSM for STP
                data_parsed = connection.send_command(
                    command_string=spanning_tree_command, use_textfsm=True
                )
                # print(f"\ndata_parsed for {host}:\n", data_parsed)

                # Finding root bridge
                root_bridge_data = find_root_bridge(netmiko_device, data_raw, prompt)

                # Captura raw output for CDP
                data_raw_cdp = connection.send_command(
                    command_string=cdp_neighbors_command, use_textfsm=False
                )
                print(f"\ndata_raw_cdp for {host}:\n", data_raw_cdp)

                # Get parsed data with TextFSM for CDP
                data_parsed_cdp = connection.send_command(
                    command_string=cdp_neighbors_command, use_textfsm=True
                )
                print(f"\ndata_parsed_cdp for {host}:\n", data_parsed_cdp)

            return (
                host,
                data_raw,
                data_parsed,
                None,
                prompt,
                root_bridge_data,
                data_raw_cdp,
                data_parsed_cdp,
            )
        except NetMikoAuthenticationException as e:
            print(f"\nFailed to connect to {host}: {port} - Authentication failed.")
            return host, None, None, "auth", None, None, None, None
        except NetMikoTimeoutException as e:
            print(
                f"\nFailed to connect to {host}: {port} - TCP connection to device failed."
            )
            return host, None, None, "timeout", prompt, root_bridge_data, None, None
        except Exception as e:
            print(
                f"\nFailed to connect to {host}: {port} - on attempt {attempt + 1}: {e}"
            )
            time.sleep(2)  # Wait a bit before retrying
    return host, None, None, "other", prompt, root_bridge_data, None, None


def main():
    # 1. Load credentials
    CREDENTIALS_FILE = "./device_credentials.json"
    try:
        with open(CREDENTIALS_FILE, "r") as file:
            devices = json.load(file)
    except FileNotFoundError:
        print(f"Error: The file {CREDENTIALS_FILE} was not found")
        return

    # 2. Establish connection to each device
    # Counters for connections
    successful_connections = 0
    failed_connections = 0
    auth_failures = 0
    timeout_failures = 0
    other_failures = 0

    # Dictionaries for saving data, prompts and information on root bridge
    stp_data_raw = {}
    stp_data_parsed = {}
    prompts = {}
    root_bridge_information = {}
    cdp_data_raw = {}
    cdp_data_parsed = {}

    # Use ThreadPoolExecutor to connect to multiple devices concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_device = {
            executor.submit(get_stp_data, device): device for device in devices
        }
        for future in as_completed(future_to_device):
            (
                host,
                data_raw,
                data_parsed,
                error_type,
                prompt,
                root_bridge_data,
                data_raw_cdp,
                data_parsed_cdp,
            ) = future.result()

            # Save prompt and host as key:value pairs in a dictionary
            prompts[prompt] = host

            # Save root bridge information if found
            if root_bridge_data is not None:
                root_bridge_information["prompt"] = root_bridge_data.get("prompt")
                root_bridge_information["host"] = root_bridge_data.get("host")
                root_bridge_information["operating_system"] = root_bridge_data.get(
                    "operating_system"
                )

            # Save raw and parsed data of all devices. Increase OK counter
            if data_raw:
                stp_data_raw[host] = data_raw
                stp_data_parsed[host] = data_parsed
                successful_connections += 1
            else:  # Increase NOK counter and Increase specific error counter
                failed_connections += 1
                if error_type == "auth":
                    auth_failures += 1
                elif error_type == "timeout":
                    timeout_failures += 1
                else:
                    other_failures += 1

            if data_raw_cdp:
                cdp_data_raw[host] = data_raw_cdp
                cdp_data_parsed[host] = data_parsed_cdp

    # End of connections
    print("\nTime to show the collected information")

    # print("\nstp_data_raw:\n", stp_data_raw)
    # print("Size: ", len(stp_data_raw))
    # print("Type: ", type(stp_data_raw))

    # Print the collected STP data using pprint
    print("\nCollected STP data:")
    print("\nstp_data_parsed:\n")
    pprint(stp_data_parsed)
    print("Size: ", len(stp_data_parsed))
    print("Type: ", type(stp_data_parsed))

    # 3. Print statistics on connections
    print(f"\nSummary of connections:")
    total_devices = len(devices)
    print(f"\n{total_devices} devices found in {CREDENTIALS_FILE} file")
    print(f"--Successful connections: {successful_connections}")
    print(f"--Failed connections: {failed_connections}")
    print(f"  --Authentication failures: {auth_failures}")
    print(f"  --Timeout failures: {timeout_failures}")
    print(f"  --Other failures: {other_failures}")

    if successful_connections == 0:
        print("\nEnd of execution")
        return

    # 4. Process the data further as needed
    print("\nPrompts:\n", prompts)

    # 5. Root Bridge info
    print("\nRoot bridge information:\n", root_bridge_information)

    # 6. CDP
    print("\nCollected CDP data:")
    print("\ncdp_data_raw:\n")
    pprint(cdp_data_raw)

    print("\ncdp_data_parsed:\n")
    pprint(cdp_data_parsed)

    # 7.
    tree_structure = {}


if __name__ == "__main__":
    start_total = time.time()
    main()
    end_total = time.time() - start_total
    print_execution_time(end_total)
