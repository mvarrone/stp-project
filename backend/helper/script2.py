import re


def extract_bridge_id(input_text):
    bridge_id = {}
    in_bridge_id_section = False

    # Split the input text into lines
    lines = input_text.split("\n")

    # Process each line
    for line in lines:
        line = line.strip()

        # Check for Bridge ID
        if line.startswith("Bridge ID"):
            in_bridge_id_section = True
            # Extract the priority
            priority_match = re.search(r"Priority\s+(\d+)", line)
            if priority_match:
                bridge_id["priority"] = priority_match.group(1)
            continue

        # If we're in the Bridge ID section, look for the Address
        if in_bridge_id_section:
            if line.startswith("Address"):
                # Extract the address
                address_match = re.search(r"Address\s+([0-9a-fA-F.]+)", line)
                if address_match:
                    bridge_id["address"] = address_match.group(1)
                    break  # We've found the address, so we can stop processing
            elif line.strip() == "":
                # If we encounter an empty line, we've moved past the Bridge ID section
                break

    return bridge_id


# Format the extracted information
def format_bridge_id(bridge_id):
    formatted_output = ["Bridge ID"]
    for key, value in bridge_id.items():
        formatted_output.append(f"  {key:<10} {value}")
    return "\n".join(formatted_output)


# Example usage
input_text = """
VLAN0001
  Spanning tree enabled protocol rstp
  Root ID    Priority    32769
             Address     5000.5800.0200
             Cost        4
             Port        5 (GigabitEthernet1/0)
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32769  (priority 32768 sys-id-ext 1)
             Address     5042.7200.0d00
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/0               Desg FWD 4         128.1    Shr 
Gi0/1               Desg FWD 4         128.2    Shr 
Gi0/2               Desg FWD 4         128.3    Shr 
Gi0/3               Desg FWD 4         128.4    Shr 
Gi1/0               Root FWD 4         128.5    Shr 
Gi1/1               Desg FWD 4         128.6    Shr 
Gi1/2               Desg FWD 4         128.7    Shr 
Gi1/3               Desg FWD 4         128.8    Shr 
"""

extracted_info = extract_bridge_id(input_text)
print(extracted_info)

formatted_output = format_bridge_id(extracted_info)
print(formatted_output)
