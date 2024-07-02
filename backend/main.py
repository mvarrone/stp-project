import json
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pprint import pprint
from typing import List, Dict, Any

from netmiko import (
    ConnectHandler,
    NetMikoAuthenticationException,
    NetMikoTimeoutException,
)
from netmiko.utilities import get_structured_data


def find_root_bridge(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    root_bridge_data: Dict[str, Any] = {
        "device": "",
        "port": "",
        "device_type": "",
        "prompt": "",
    }

    CISCO_STP_RAW_OUTPUT_ROOT_BRIDGE_TEXT = "This bridge is the root"

    for result in results:
        if result.get("device_type") == "cisco_ios":
            if CISCO_STP_RAW_OUTPUT_ROOT_BRIDGE_TEXT in result.get("stp_output_raw"):
                root_bridge_data["device"] = result.get("device")
                root_bridge_data["port"] = result.get("port")
                root_bridge_data["device_type"] = result.get("device_type")
                root_bridge_data["prompt"] = result.get("prompt")
                return root_bridge_data

    root_bridge_data = {}
    return root_bridge_data


def get_prompt(connection, device_type):
    if device_type == "cisco_ios":
        prompt = connection.find_prompt()
        # print(f"{prompt = }")
        if not prompt:
            return "prompt not found"

        if prompt[-1] == "#":
            prompt = prompt[:-1]

        # print(f"{prompt = }")
        return prompt

    prompt = connection.find_prompt()
    return prompt


def print_execution_time(end_total: float) -> None:
    if end_total > 1:
        print(f"\nTotal script execution time: {end_total:.2f} s")
    else:
        end_total *= 1000
        print(f"\nTotal script execution time: {end_total:.2f} ms")


def load_credentials(CREDENTIALS_FILE: str) -> List[Dict[str, Any]]:
    devices: List[Dict[str, Any]] = []
    try:
        with open(CREDENTIALS_FILE, "r") as file:
            devices = json.load(file)
    except FileNotFoundError:
        print(f"Error: File {CREDENTIALS_FILE} was not found")
        return devices
    return devices


def connect_to_device(device: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "device": device.get("host", ""),
        "port": device.get("port", ""),
        "device_type": device.get("device_type", ""),
        "prompt": "",
        "status": "success",
        "stp_output_raw": "",
        "stp_output_parsed": "",
        "cdp_output_raw": "",
        "cdp_output_parsed": "",
    }

    spanning_tree_command = device.get("spanning_tree_command", "show spanning-tree")
    cdp_neighbors_command = device.get("cdp_neighbors_command", "show cdp neighbors")

    netmiko_device = {
        k: v
        for k, v in device.items()
        if k not in ["spanning_tree_command", "cdp_neighbors_command"]
    }

    try:
        with ConnectHandler(**netmiko_device) as connection:
            if "secret" in netmiko_device:
                connection.enable()  # Enter privileged EXEC mode

            # Get prompt for each device
            result["prompt"] = get_prompt(connection, netmiko_device.get("device_type"))

            # Get raw STP data
            result["stp_output_raw"] = connection.send_command(
                command_string=spanning_tree_command
            )
            # Parse STP data locally
            result["stp_output_parsed"] = get_structured_data(
                result["stp_output_raw"],
                platform=connection.device_type,
                command=spanning_tree_command,
            )

            # Get raw CDP data
            result["cdp_output_raw"] = connection.send_command(
                command_string=cdp_neighbors_command
            )
            # Parse CDP data locally
            result["cdp_output_parsed"] = get_structured_data(
                result["cdp_output_raw"],
                platform=connection.device_type,
                command=cdp_neighbors_command,
            )

    except NetMikoAuthenticationException:
        result["status"] = "authentication_failure"
    except NetMikoTimeoutException:
        result["status"] = "timeout"
    except Exception as e:
        result["status"] = f"other_failure:{str(e)}"
    return result


def main() -> None:
    # 1. Load credentials
    CREDENTIALS_FILE: str = "./device_credentials.json"

    devices: List[Dict[str, Any]] = load_credentials(CREDENTIALS_FILE)
    if not devices:
        sys.exit(1)
    total_devices: int = len(devices)
    print(f"{total_devices} devices found in {CREDENTIALS_FILE} file")

    # 2. Connect to devices concurrently
    results: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=total_devices) as executor:
        future_to_device = {
            executor.submit(connect_to_device, device): device for device in devices
        }
        for future in as_completed(future_to_device):
            results.append(future.result())

    print("\nDEBUG:")
    for result in results:
        pprint(result)

    # 3. Count successes and failures
    connection_counter: Counter = Counter()
    for result in results:
        connection_counter[result.get("status", "unknown")] += 1

    # 4. Print results
    print("\nSummary of connections:")
    total_devices = len(devices)
    successful_connections = connection_counter.get("success", 0)
    print(f"  Successful connections: {successful_connections}/{total_devices}")
    failed_connections = total_devices - successful_connections
    print(f"  Failed connections: {failed_connections}/{total_devices}")

    # Define all possible statuses for failed connections
    all_statuses = {"authentication_failure", "timeout", "other_failure"}
    for status in sorted(all_statuses):
        count = connection_counter.get(status, 0)
        print(f"    {status}: {count}/{total_devices}")

    if not successful_connections:
        print("\nNo successful connections were made. Ending here")
        return

    # 5. Find root bridge
    root_bridge_data = find_root_bridge(results)
    if not root_bridge_data:
        print("\nNo root bridge found. Ending here")
        return
    print(f"\n5. Root bridge has been found:\n{root_bridge_data}")


if __name__ == "__main__":
    start_total: float = time.time()
    main()
    end_total: float = time.time() - start_total
    print_execution_time(end_total)
