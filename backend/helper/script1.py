import re


def extract_vlan_info(input_text):
    # Initialize variables to store the extracted information
    vlan_info = {}
    current_vlan = None

    # Split the input text into lines
    lines = input_text.split("\n")

    # Process each line
    for line in lines:
        line = line.strip()

        # Check for VLAN
        vlan_match = re.match(r"VLAN(\d+)", line)
        if vlan_match:
            current_vlan = vlan_match.group(1)
            vlan_info[current_vlan] = {"Root ID": {}, "Bridge ID": {}}
            continue

        # Check for Root ID or Bridge ID
        if current_vlan:
            if line.startswith("Root ID") or line.startswith("Bridge ID"):
                current_id = "Root ID" if line.startswith("Root ID") else "Bridge ID"
                # Extract the priority
                priority_match = re.search(r"Priority\s+(\d+)", line)
                if priority_match:
                    vlan_info[current_vlan][current_id]["Priority"] = (
                        priority_match.group(1)
                    )
            elif line.startswith("Address"):
                # Extract the address
                address_match = re.search(r"Address\s+([0-9a-fA-F.]+)", line)
                if address_match:
                    vlan_info[current_vlan][current_id]["Address"] = (
                        address_match.group(1)
                    )

    return vlan_info


# Format the extracted information
def format_vlan_info(vlan_info):
    formatted_output = []
    for vlan, data in vlan_info.items():
        formatted_output.append(f"VLAN{vlan}")
        for id_type in ["Root ID", "Bridge ID"]:
            if data[id_type]:
                formatted_output.append(f"  {id_type}")
                for key, value in data[id_type].items():
                    formatted_output.append(f"    {key:<10} {value}")
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

extracted_info = extract_vlan_info(input_text)
print(extracted_info)

formatted_output = format_vlan_info(extracted_info)
print(formatted_output)

print(20 * "*")

input_text_2 = """
VLAN0001
  Spanning tree enabled protocol rstp
  Root ID    Priority    32769
             Address     5000.5800.0200
             This bridge is the root
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
  Bridge ID  Priority    32769  (priority 32768 sys-id-ext 1)
             Address     5000.5800.0200
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type     
------------------- ---- --- --------- -------- --------------------------------
Gi0/0               Desg FWD 4         128.1    Shr      
Gi0/1               Desg FWD 4         128.2    Shr      
Gi0/2               Desg FWD 4         128.3    Shr      
Gi0/3               Desg FWD 4         128.4    Shr      
Gi1/0               Desg FWD 4         128.5    Shr      
Gi1/1               Desg FWD 4         128.6    Shr      
Gi1/2               Desg FWD 4         128.7    Shr      
Gi1/3               Desg FWD 4         128.8    Shr      
"""

extracted_info_2 = extract_vlan_info(input_text_2)
print(extracted_info_2)

formatted_output_2 = format_vlan_info(extracted_info_2)
print(formatted_output_2)
