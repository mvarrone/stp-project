import json
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

# Variables
CREDENTIALS_FILE: str = "./device_credentials.json"
SENTINEL_VALUE_FOR_LEVEL: int = 9999
connection_id: int = 0

def print_node_structure(nodes) -> None:
    # Sort nodes by key 'level'
    sorted_nodes = sorted(nodes, key = lambda x: x.get("level"))

    # Print the network tree structure
    print("\nOption 1: Network Tree Structure")
    print(32 * '-')
    # Option 1
    for sorted_node in sorted_nodes:
        indent = 2 * '-' * sorted_node.get("level")
        print(f"{indent}{sorted_node.get("label")} - {sorted_node.get("title")}, Level: {sorted_node.get("level")}")

    print("\nOption 2: Network Tree Structure")
    print(32 * '-')
    # Option 2
    for sorted_node in sorted_nodes:
        indent = 2 * ' ' * sorted_node.get("level")
        print(f"({sorted_node.get("level")}) | {indent}{sorted_node.get("label")} - {sorted_node.get("title")}")


def process_nodes(root_bridge_data, results) -> List[Dict[str, Any]]:
    # Level 0: Node for Root Bridge
    def calculate_node_for_level_0(root_bridge_data) -> List[Dict[str, Any]]:
        nodes = []
        node = {
            "id": root_bridge_data.get("id"),
            "label": root_bridge_data.get("label"),
            "level": root_bridge_data.get("level"),
            "title": root_bridge_data.get("title")
        }
        nodes.append(node)
        return nodes
    
    nodes = calculate_node_for_level_0(root_bridge_data)
    print("\nLevel 0 - nodes:\n", nodes)

    # Once the root bridge node has been added, let's proceed with root bridge neighbors
    # Level 1: Nodes for Root Bridge neighbors
    def calculate_nodes_for_level_1(nodes, root_bridge_data, results) -> List[Dict[str, Any]]:
        root_bridge_neighbor_list = []
        root_bridge_neighbors = root_bridge_data.get("neighbors")

        for neighbor in root_bridge_neighbors:
            neighbor_name = neighbor.get("neighbor").split(".")[0]
            root_bridge_neighbor_list.append(neighbor_name)
        print("\nroot_bridge_neighbor_list:\n", root_bridge_neighbor_list)
        
        for root_bridge_neighbor in root_bridge_neighbor_list:
            for result in results:
                if root_bridge_neighbor == result.get("prompt"):
                    node = {
                        "id": result.get("id"),
                        "label": result.get("label"),
                        "level": 1, # 1 because this node is a root bridge neighbor
                        "title": result.get("title")
                    }
                    nodes.append(node)
                    result["level"] = 1
        return nodes

    nodes = calculate_nodes_for_level_1(nodes, root_bridge_data, results)
    print("\nLevel 1 - nodes:\n", nodes)

    # Level > 1: Remaining nodes
    print("\nFunction: calculate_nodes_with_level_higher_than_1()")
    def calculate_nodes_with_level_higher_than_1(nodes) -> List[Dict[str, Any]]:
        current_level = max(node.get("level") for node in nodes)
        #print("\ncurrent_level:", current_level)

        nodes_to_analize = [
            node for node in nodes if node.get("level") == current_level
        ]

        print(f"\nnodes to analize because we are in level {current_level}")
        print("nodes to analize:", nodes_to_analize)

        neighbors_data = []
        for node in nodes_to_analize:
            node_name = node.get("label")
            #print("\nnode name to analize:", node_name)
            for result in results:
                if result.get("label") == node_name:
                    neighbors = result.get("cdp_output_parsed")
                    #print("\nneighbors:", neighbors)
                    for neighbor in neighbors:
                        neighbor_name = neighbor.get("neighbor").split(".")[0]
                        #print("--", neighbor_name)
                        neighbors_data.append(neighbor_name)
        
        for neighbor in neighbors_data:
            #print("\nneighbor:", neighbor)
            for result in results:
                if result.get("label") == neighbor:
                    level_found = result.get("level")
                    #print("\nlevel_found:", level_found, "\n")
                    if level_found == SENTINEL_VALUE_FOR_LEVEL:
                        updated_level = current_level + 1
                        result["level"] = updated_level
                        #print(f"{neighbor}: Level changed from {level_found} to {updated_level}")
                        node = {
                            "id": result.get("id"),
                            "label": result.get("label"),
                            "level": updated_level,
                            "title": result.get("title")
                        }
                        nodes.append(node)

        #print("\nresults:", results)
        print("\nnodes:\n", nodes)
        return nodes
    
    for i in range(1, 10):
        print(f"\nIteration {i = }")
        nodes = calculate_nodes_with_level_higher_than_1(nodes)
    return nodes

                            
def find_root_bridge(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    root_bridge_data: Dict[str, Any] = {
        "device": "",
        "device_type": "",
        "prompt": "",
        "level": "",
        "id": "",
        "label": "",
        "title": "",
        "neighbors": ""
    }

    CISCO_STP_RAW_OUTPUT_ROOT_BRIDGE_TEXT = "This bridge is the root"

    for result in results:
        if result.get("device_type") == "cisco_ios":
            if CISCO_STP_RAW_OUTPUT_ROOT_BRIDGE_TEXT in result.get("stp_output_raw"):
                root_bridge_data["device"] = result.get("device")
                root_bridge_data["device_type"] = result.get("device_type")
                root_bridge_data["prompt"] = result.get("prompt")
                root_bridge_data["level"] = 0 # 0 because this node is the root bridge and that is why it has level 0
                root_bridge_data["id"] = result.get("id")
                root_bridge_data["label"] = result.get("label")
                root_bridge_data["title"] = result.get("title")
                root_bridge_data["neighbors"] = result.get("cdp_output_parsed")
                result["level"] = 0
                return root_bridge_data

    root_bridge_data = {}
    return root_bridge_data


def get_prompt(connection, device_type) -> str:
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
        "id": "",
        "label": "",
        "title": "",
        "level": "",
    }

    global connection_id # The connection_id variable is used as a counter for each device connection and is later used in the nodes variable.

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
                raw_output=result.get("stp_output_raw"),
                platform=connection.device_type,
                command=spanning_tree_command,
            )

            # Get raw CDP data
            result["cdp_output_raw"] = connection.send_command(
                command_string=cdp_neighbors_command
            )

            # Parse CDP data locally
            result["cdp_output_parsed"] = get_structured_data(
                raw_output=result.get("cdp_output_raw"),
                platform=connection.device_type,
                command=cdp_neighbors_command,
            )

            # Assign ID to each device for being used in nodes later
            result["id"] = connection_id

            # Assign a label to each device for being used in nodes later
            # label is the exact info as prompt
            result["label"] = result.get("prompt")

            # Assign a title to each device for being used in nodes later
            result["title"] = f"{device.get("host")} - {device.get("device_type")}"
            
            # Assign a SENTINEL_VALUE_FOR_LEVEL to each device for being used in nodes later
            # SENTINEL_VALUE_FOR_LEVEL: It indicates that the key level has not yet been determined
            # It will be updated in the process_nodes function later
            result["level"] = SENTINEL_VALUE_FOR_LEVEL

            # Increase ID
            connection_id += 1
    except NetMikoAuthenticationException:
        result["status"] = "authentication_failure"
    except NetMikoTimeoutException:
        result["status"] = "timeout"
    except Exception as e:
        result["status"] = f"other_failure:{str(e)}"
    return result


def main() -> None:
    # 1. Load credentials
    print("1. Load credentials")
    devices: List[Dict[str, Any]] = load_credentials(CREDENTIALS_FILE)
    if not devices:
        return

    total_devices: int = len(devices)
    if total_devices == 1:
        print(f"1 device found in {CREDENTIALS_FILE} file")
    else:
        print(f"{total_devices} devices found in {CREDENTIALS_FILE} file")

    # 2. Connect to devices concurrently
    print("\n2. Connect to devices concurrently")
    results: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=total_devices) as executor:
        future_to_device = {
            executor.submit(connect_to_device, device): device for device in devices
        }
        for future in as_completed(future_to_device):
            results.append(future.result())

    print("DEBUG:")
    for result in results:
        pprint(result) 

    # 3. Count successes and failures
    print("\n3. Count successes and failures")
    connection_counter: Counter = Counter()
    for result in results:
        connection_counter[result.get("status", "unknown")] += 1
    print("Done")

    # 4. Print results
    print("\n4. Print results\n\nSummary of connections:")
    total_devices = len(devices)
    successful_connections = connection_counter.get("success", 0)
    successful_connections_percentaje = 100 * successful_connections / total_devices
    print(f"--Successful connections: {successful_connections}/{total_devices} ({successful_connections_percentaje} %)")
    failed_connections = total_devices - successful_connections
    failed_connections_percentaje = 100 * failed_connections / total_devices
    print(f"--Failed connections: {failed_connections}/{total_devices} ({failed_connections_percentaje} %)")

    # Define all possible statuses for failed connections
    all_statuses = {"authentication_failure", "timeout", "other_failure"}
    for status in sorted(all_statuses):
        count = connection_counter.get(status, 0)
        print(f"----{status}: {count}/{total_devices}")

    if not successful_connections:
        print("\nNo successful connections were made. Ending here")
        return

    # 5. Find root bridge
    print("\n5. Find root bridge")
    root_bridge_data = find_root_bridge(results)
    if not root_bridge_data:
        print("\nNo root bridge found. Ending here")
        return
    print(f"\nRoot bridge has been found:\n{root_bridge_data}")

    # 6. Build nodes
    print("\n6. Build nodes")
    nodes = process_nodes(root_bridge_data, results)
    #print(nodes)
    print("\nBetter way to show nodes:")
    for node in nodes:
        print(node)

    # 7. Print node tree structure
    print("\n7. Print node tree structure")
    print_node_structure(nodes)

if __name__ == "__main__":
    start_total: float = time.time()
    main()
    end_total: float = time.time() - start_total
    print_execution_time(end_total)
