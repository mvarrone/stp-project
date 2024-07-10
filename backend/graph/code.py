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


def print_updated_edge_information(final_edges) -> None:
    #print(final_edges)
    print("\nBetter way to show final_edges:")
    for edge in final_edges:
        print(edge)

def remove_blocked_links(edges_to_be_deleted, edges_without_duplicated) -> List[Dict[str, int]]:
    m = len(edges_to_be_deleted)
    if m == 1:
        print("We found that 1 edge must be deleted")
    else:
        print(f"We found that {m} edges must be deleted")
    
    print("edges_to_be_deleted: ", edges_to_be_deleted)

    print(f"\nedges_without_duplicated: {len(edges_without_duplicated)} element(s)")
    print(edges_without_duplicated)

    for edge in edges_to_be_deleted:
        # Create the opposite edge dictionary
        opposite_edge = {'from': edge.get("to"), 'to': edge.get("from")}
        
        # Try to remove the original edge if it exists
        if edge in edges_without_duplicated:
            edges_without_duplicated.remove(edge)
        
        # Try to remove the opposite edge if it exists
        if opposite_edge in edges_without_duplicated:
            edges_without_duplicated.remove(opposite_edge)
    
    edges = edges_without_duplicated
    print(f"\nedges: {len(edges)} element(s)")
    print(edges)
    return edges

def identify_blocked_links(results: List[Dict[str, Any]]) -> List[Dict[str, int]]:
    edges_to_be_deleted = []

    for result in results:
        #device_prompt = result.get("prompt")
        device_id = result.get("id")
        stp_output = result.get("stp_output_parsed", [])
        cdp_output = result.get("cdp_output_parsed", [])

        # Step 1: Identify interfaces with Role=Altn
        altn_interfaces = [entry for entry in stp_output if entry.get("role") == "Altn"]
        #print("\naltn_interfaces", altn_interfaces)

        for altn_interface in altn_interfaces:
            interface_name = altn_interface.get("interface")
            #print("\ninterface_name", interface_name)

            # Step 2: Find matching CDP entry
            matching_cdp_entry = next((entry for entry in cdp_output if entry.get("local_interface") == interface_name), None)
            #print("\nmatching_cdp_entry", matching_cdp_entry)

            if matching_cdp_entry:
                neighbor_name = matching_cdp_entry.get("neighbor")
                #print("\nneighbor_name", neighbor_name)

                # Step 3: Find neighbor device ID
                neighbor_device = next((dev for dev in results if dev.get("prompt") == neighbor_name), None)
                #print("\nneighbor_device", neighbor_device)

                if neighbor_device:
                    neighbor_id = neighbor_device.get("id")

                    # Step 4: Create edge dictionary
                    edge = {
                        "from": device_id,
                        "to": neighbor_id
                    }
                    edges_to_be_deleted.append(edge)
    return edges_to_be_deleted

def print_edge_information(edges, edges_with_names, switches, edges_without_duplicated, edges_without_duplicated_with_names) -> None:
    #print(switches)
    print(f"\nBetter way to show switches:\nSwitch references")
    for switch in switches:
        print(switch)

    #print(edges)
    print("\nBetter way to show edges:")
    for edge in edges:
        print(edge)
        
    #print(edges_with_names)
    print("\nBetter way to show edges_with_names:")
    for edges_with_name in edges_with_names:
        print(edges_with_name)

    #print(edges_without_duplicated)
    print("\nBetter way to show edges_without_duplicated:")
    for edge_wo in edges_without_duplicated:
        print(edge_wo)

    #print(edges_without_duplicated_with_names)
    print("\nBetter way to show edges_without_duplicated_with_names:")
    for edge_wo_with_name in edges_without_duplicated_with_names:
        print(edge_wo_with_name)

def process_edges(results) -> List[Dict[str, Any]]:
    edges: List[Dict[str, int]] = []
    edges_with_names: List[Dict[str, str]] = []
    switches: List[Dict[str, Any]] = []
    edges_without_duplicated: List[Dict[str, int]] = []
    edges_without_duplicated_with_names: List[Dict[str, str]] = []

    seen_edges = set()

    # Extracting edges from results
    for result in results:
        switch_name = result.get("prompt")
        switch_id = result.get("id")
        cdp_data = result.get("cdp_output_parsed")

        switch = {'name': switch_name, 'id': switch_id}   
        switches.append(switch)

        for entry in cdp_data:
            neighbor_prompt = entry.get("neighbor")
            edge_with_name = {'from': switch_name, 'to': neighbor_prompt}
            edges_with_names.append(edge_with_name)

            neighbor_id = None
            # Find neighbor id based on neighbor prompt
            for neighbor_switch in results:
                if neighbor_switch.get("prompt") == neighbor_prompt:
                    neighbor_id = neighbor_switch.get("id")
                    break
            
            if neighbor_id is not None:
                edge = {'from': switch_id, 'to': neighbor_id}
                edges.append(edge)

                # Create a tuple for the edge to check for duplicates
                edge_tuple = tuple(sorted((switch_id, neighbor_id)))
                if edge_tuple not in seen_edges:
                    seen_edges.add(edge_tuple)
                    edge_wo = {'from': switch_id, 'to': neighbor_id}
                    edges_without_duplicated.append(edge_wo)
                    edges_without_duplicated_with_names.append({'from': switch_name, 'to': neighbor_prompt})


    return edges, edges_with_names, switches, edges_without_duplicated, edges_without_duplicated_with_names

def print_node_information(nodes) -> None:
    #print(nodes)
    print("\nBetter way to show nodes:")
    for node in nodes:
        print(node)

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
    #print("\nLevel 0 - nodes:\n", nodes)

    # Once the root bridge node has been added, let's proceed with root bridge neighbors
    # Level 1: Nodes for Root Bridge neighbors
    def calculate_nodes_for_level_1(nodes, root_bridge_data, results) -> List[Dict[str, Any]]:
        root_bridge_neighbor_list = []
        root_bridge_neighbors = root_bridge_data.get("neighbors")

        for neighbor in root_bridge_neighbors:
            #neighbor_name = neighbor.get("neighbor").split(".")[0]
            neighbor_name = neighbor.get("neighbor")
            root_bridge_neighbor_list.append(neighbor_name)
        #print("\nroot_bridge_neighbor_list:\n", root_bridge_neighbor_list)
        
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
                    result["level"] = 1 # Update results dictionary changing from 9999 to 1 for root bridge neighbors level value
        return nodes

    nodes = calculate_nodes_for_level_1(nodes, root_bridge_data, results)
    #print("\nLevel 1 - nodes:\n", nodes)

    # Level > 1: Remaining nodes
    #print("\nFunction: calculate_nodes_with_level_higher_than_1()")
    def calculate_nodes_with_level_higher_than_1(nodes) -> List[Dict[str, Any]]:
        current_level = max(node.get("level") for node in nodes)
        #print("\ncurrent_level:", current_level)

        nodes_to_analize = [
            node for node in nodes if node.get("level") == current_level
        ]

        #print(f"\nnodes to analize because we are in level {current_level}")
        #print("nodes to analize:", nodes_to_analize)

        neighbors_data = []
        for node in nodes_to_analize:
            node_name = node.get("label")
            #print("\nnode name to analize:", node_name)
            for result in results:
                if result.get("label") == node_name:
                    neighbors = result.get("cdp_output_parsed")
                    #print("\nneighbors:", neighbors)
                    for neighbor in neighbors:
                        #neighbor_name = neighbor.get("neighbor").split(".")[0]
                        neighbor_name = neighbor.get("neighbor")
                        #print("--", neighbor_name)
                        neighbors_data.append(neighbor_name)
        
        for neighbor in neighbors_data:
            #print("\nneighbor:", neighbor)
            for result in results:
                if result.get("label") == neighbor:
                    level_found = result.get("level")
                    #print("\nlevel_found:", level_found, "\n")
                    if level_found == 9999:
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
        #print("\nnodes:\n", nodes)
        return nodes
    
    for i in range(1, 10):
        #print(f"\nIteration {i = }")
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
                result["level"] = 0 # Update results dictionary changing from 9999 to 0 for root bridge level value
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


def print_execution_time(end_total: float):
    end_total = round(end_total, 2)

    if end_total > 1:
        unit = "s"
        print(f"\nTotal script execution time: {end_total} {unit}")
    else:
        unit = "ms"
        end_total *= 1000
        print(f"\nTotal script execution time: {end_total} {unit}")
    
    return end_total, unit


def load_credentials(CREDENTIALS_FILE: str) -> List[Dict[str, Any]]:
    devices: List[Dict[str, Any]] = []
    try:
        with open(CREDENTIALS_FILE, "r") as file:
            devices = json.load(file)
    except FileNotFoundError:
        print(f"Error: File {CREDENTIALS_FILE} was not found")
        return devices
    return devices

def modify_stp_parsed_data(parsed_stp_output, device_type) -> List[Dict[str, str]]:
    if device_type == "cisco_ios":
        for entry in parsed_stp_output:
            if 'interface' in entry:
                entry['interface'] = entry['interface'].replace('Gi', 'G ')

        return parsed_stp_output


def modify_cdp_parsed_data(parsed_cdp_output, device_type) -> List[Dict[str, str]]:
    if device_type == "cisco_ios":
        for entry in parsed_cdp_output:
            if 'neighbor' in entry:
                entry['neighbor'] = entry['neighbor'].split('.')[0]

            if 'capability' in entry:
                entry['capability'] = entry['capability'].strip()

            if 'local_interface' in entry:
                entry['local_interface'] = entry['local_interface'].replace('Gig ', 'G ')
            
            if 'neighbor_interface' in entry:
                entry['neighbor_interface'] = entry['neighbor_interface'].replace('Gig ', 'G ')   

        return parsed_cdp_output

def connect_to_device(device: Dict[str, Any]) -> Dict[str, Any]:
    global connection_id

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

            device_type = netmiko_device.get("device_type")

            # Get prompt for each device
            result["prompt"] = get_prompt(connection, device_type)

            # Get raw STP data
            result["stp_output_raw"] = connection.send_command(
                command_string=spanning_tree_command
            )

            # Parse STP data locally
            parsed_stp_output = get_structured_data(
                raw_output=result.get("stp_output_raw"),
                platform=connection.device_type,
                command=spanning_tree_command,
            )

            # Post processing for STP parsed data 
            parsed_stp_output = modify_stp_parsed_data(parsed_stp_output, device_type)

            # Assign post processed data to dictionary
            result["stp_output_parsed"] = parsed_stp_output

            # Get raw CDP data
            result["cdp_output_raw"] = connection.send_command(
                command_string=cdp_neighbors_command
            )

            # Parse CDP data locally
            parsed_cdp_output = get_structured_data(
                raw_output=result.get("cdp_output_raw"),
                platform=connection.device_type,
                command=cdp_neighbors_command,
            )

            # Post processing for CDP parsed data 
            parsed_cdp_output = modify_cdp_parsed_data(parsed_cdp_output, device_type)

            # Assign post processed data to dictionary
            result["cdp_output_parsed"] = parsed_cdp_output

            # Assign ID to each device for being used in nodes later
            result["id"] = connection_id

            # Assign a label to each device for being used in nodes later
            # label is the exact info as prompt
            result["label"] = result.get("prompt")

            # Assign a title to each device for being used in nodes later
            result["title"] = f"SVI: {device.get("host")} - Platform: {device.get("device_type")}"
            
            # Assign a value of 9999 to each device for being used in nodes later
            # Value of 9999: It indicates that the key level has not yet been determined
            # It will be updated in the process_nodes function later
            # All devices start having a value of 9999
            # When root bridge is found, that device gets a value of 0
            # When root bridge neighbor(s) is/are found, that/those device(s) will get a value of 1
            result["level"] = 9999

            # Increase ID
            connection_id += 1
    except NetMikoAuthenticationException:
        result["status"] = "authentication_failure"
    except NetMikoTimeoutException:
        result["status"] = "timeout"
    except Exception as e:
        result["status"] = f"other_failure:{str(e)}"
    return result


def main():
    global connection_id
    connection_id = 0

    # 1. Load credentials
    print("1. Load credentials")
    CREDENTIALS_FILE: str = "./device_credentials.json"
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
    successful_connections: List[str] = []
    failed_connections: Dict[str, List[str]] = {
        "authentication_failure": [],
        "timeout": [],
        "other_failure": []
    }
    for result in results:
        status = result.get("status", "unknown")
        connection_counter[status] += 1
        device_info = f"{result['prompt']} - {result['device']}"
        if status == "success":
            successful_connections.append(device_info)
        else:
            failed_connections[status].append(device_info)
    print("Done")

    # 4. Print results
    print("\n4. Print results\n\nSummary of connections:")
    total_devices = len(devices)
    successful_count = connection_counter.get("success", 0)
    successful_percentage = 100 * successful_count / total_devices
    print(f"--Successful connections: {successful_count}/{total_devices} ({successful_percentage:.1f}%)")
    if successful_count > 0:
        for device in successful_connections:
            print(f"    {device}")

    failed_count = total_devices - successful_count
    failed_percentage = 100 * failed_count / total_devices
    print(f"--Failed connections: {failed_count}/{total_devices} ({failed_percentage:.1f}%)")

    all_statuses = {"authentication_failure", "timeout", "other_failure"}
    for status in sorted(all_statuses):
        count = connection_counter.get(status, 0)
        print(f"  --{status}: {count}/{total_devices}")
        if count > 0:
            for device in failed_connections[status]:
                print(f"      {device}")

    if not successful_count:
        print("\nNo successful connections were made. Ending here")
        data = {
            "nodes": [],
            "edges": [],
        }
        return data

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
    print("Done")

    # 7. Print node information
    print("\n7. Print node information")
    print_node_information(nodes)

    # 8. Print node tree structure
    print("\n8. Print node tree structure")
    print_node_structure(nodes)

    # 9. Build edges
    print("\n9. Build edges")
    edges, edges_with_names, switches, edges_without_duplicated, edges_without_duplicated_with_names = process_edges(results)
    print("Done")

    # 10. Print edge information
    print("\n10. Print edge information")
    print_edge_information(edges, edges_with_names, switches, edges_without_duplicated, edges_without_duplicated_with_names)

    # 11. Identify edges where exist blocked interfaces (Role = Altn)
    print("\n11. Identify edges where exist blocked interfaces (Role = Altn)")
    edges_to_be_deleted = identify_blocked_links(results)
    print("Edges identified:", edges_to_be_deleted)

    # 12. Remove edge(s)
    print("\n12. Remove edge(s)")
    edges = remove_blocked_links(edges_to_be_deleted, edges_without_duplicated)
    
    # 13. Print updated edge information
    print("\n13. Print updated edge information")
    print_updated_edge_information(edges)

    # 14. Print final data
    print("\n14. Print final data\n") 
    data = {
        "nodes": nodes,
        "edges": edges,
    }
    print(data)
    return data

#if __name__ == "__main__":
#    start_total: float = time.time()
#    data = main()
#    end_total: float = time.time() - start_total
#    end_total, unit = print_execution_time(end_total)
