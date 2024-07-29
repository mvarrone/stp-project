import re

input_text_1 = """
VLAN0001
Spanning tree enabled protocol rstp
Root ID     Priority    32769
            Address     5000.5800.0200
            Cost        4
            Port        5 (GigabitEthernet1/0)
            Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

Bridge ID   Priority    32769  (priority 32768 sys-id-ext 1)
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

VLAN0099
Spanning tree enabled protocol rstp
Root ID     Priority    32769
            Address     5000.5800.0200
            Cost        12
            Port        5 (GigabitEthernet1/0)
            Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

Bridge ID   Priority    32769  (priority 32768 sys-id-ext 1)
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

VLAN0100
Spanning tree enabled protocol rstp
Root ID     Priority    32769
            Address     5000.5800.0200
            Cost        16
            Port        5 (GigabitEthernet1/0)
            Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

Bridge ID   Priority    32769  (priority 32768 sys-id-ext 1)
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

input_text_2 = """
VLAN0001
Spanning tree enabled protocol rstp
Root ID     Priority    32769
            Address     5000.5800.0200
            This bridge is the root
            Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
Bridge ID   Priority    32769  (priority 32768 sys-id-ext 1)
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


def parse_stp_data_per_vlan(raw_text):
    vlan_info = {}
    current_vlan = None
    current_id = None

    lines = raw_text.split("\n")

    for line in lines:
        line = line.strip()

        vlan_match = re.match(r"VLAN(\d+)", line)
        if vlan_match:
            current_vlan = vlan_match.group(1)
            vlan_info[current_vlan] = {
                "protocol": "",
                "root_id": {},
                "bridge_id": {},
            }
            continue

        if current_vlan:
            protocol_match = re.search(r"Spanning tree enabled protocol (\S+)", line)
            if protocol_match:
                vlan_info[current_vlan]["protocol"] = protocol_match.group(1)
                continue

            if line.startswith("Root ID") or line.startswith("Bridge ID"):
                current_id = "root_id" if line.startswith("Root ID") else "bridge_id"
                priority_match = re.search(r"Priority\s+(\d+)", line)
                if priority_match:
                    priority = int(priority_match.group(1))
                    vlan_info[current_vlan][current_id]["priority"] = priority
            elif line.startswith("Address"):
                address_match = re.search(r"Address\s+([0-9a-fA-F.]+)", line)
                if address_match:
                    vlan_info[current_vlan][current_id]["address"] = (
                        address_match.group(1)
                    )
            elif line.startswith("Cost"):
                cost_match = re.search(r"Cost\s+(\d+)", line)
                if cost_match:
                    cost = int(cost_match.group(1))
                    vlan_info[current_vlan][current_id]["cost"] = cost
            elif "This bridge is the root" in line:
                vlan_info[current_vlan][current_id]["cost"] = 0
            elif "Hello Time" in line:
                counters_match = re.search(
                    r"Hello Time\s+(\d+).*Max Age\s+(\d+).*Forward Delay\s+(\d+)", line
                )
                if counters_match:
                    vlan_info[current_vlan][current_id]["counters"] = {
                        "hello_time": int(counters_match.group(1)),
                        "max_age": int(counters_match.group(2)),
                        "forward_delay": int(counters_match.group(3)),
                    }
            elif line.startswith("Aging Time"):
                aging_time_match = re.search(r"Aging Time\s+(\d+)", line)
                if aging_time_match and current_id == "bridge_id":
                    if "counters" not in vlan_info[current_vlan][current_id]:
                        vlan_info[current_vlan][current_id]["counters"] = {}
                    vlan_info[current_vlan][current_id]["counters"]["aging_time"] = int(
                        aging_time_match.group(1)
                    )

    return vlan_info


def format_vlan_info(parsed_stp_data):
    formatted_output = []
    for vlan, data in parsed_stp_data.items():
        formatted_output.append(f"VLAN{vlan}")
        if "protocol" in data:
            formatted_output.append(f"  protocol     {data['protocol']}")
        for id_type in ["root_id", "bridge_id"]:
            if data[id_type]:
                formatted_output.append(f"  {id_type}")
                for key, value in data[id_type].items():
                    if key == "counters":
                        formatted_output.append("    counters")
                        for counter_key, counter_value in value.items():
                            formatted_output.append(
                                f"      {counter_key:<14} {counter_value}"
                            )
                    else:
                        formatted_output.append(f"    {key:<14} {value}")

    formatted_output = "\n".join(formatted_output)
    return formatted_output


def main():
    # texts = [input_text_1, input_text_2]
    texts = [input_text_1]
    # texts = [input_text_2]

    parsed_stp_data_list = []
    for i, raw_text in enumerate(texts, start=1):
        print(f"Processing input_text_{i}:")

        parsed_stp_data = parse_stp_data_per_vlan(raw_text)
        print("\nparsed_stp_data:\n\n", parsed_stp_data)
        parsed_stp_data_list.append(parsed_stp_data)

        formatted_output = format_vlan_info(parsed_stp_data)
        print("\nformatted_output:\n\n", formatted_output)

        print("\n", 20 * "-", "\n")

    print(f"\nparsed_stp_data_list:\n\n{(parsed_stp_data_list)}")

    vlans_found = []
    for vlan_id in parsed_stp_data_list[0]:
        # vlan_id = int(vlan_id)
        vlans_found.append(vlan_id)
    print(f"\nvlans_found: {vlans_found}")
    print(f"\nNumber of VLANs found: {len(vlans_found)}")


if __name__ == "__main__":
    main()
