from typing import List, Dict, Any


def identify_blocked_links(results: List[Dict[str, Any]]) -> List[Dict[str, int]]:
    links_to_be_deleted = []

    for result in results:
        device_prompt = result.get("prompt")
        device_id = result.get("id")
        stp_output = result.get("stp_output_parsed", [])
        cdp_output = result.get("cdp_output_parsed", [])

        # Step 1: Identify interfaces with Role=Altn
        altn_interfaces = [entry for entry in stp_output if entry.get("role") == "Altn"]

        for altn_interface in altn_interfaces:
            interface_name = altn_interface.get("interface")

            # Step 2: Find matching CDP entry
            matching_cdp_entry = next(
                (
                    entry
                    for entry in cdp_output
                    if entry.get("local_interface") == interface_name
                ),
                None,
            )

            if matching_cdp_entry:
                neighbor_name = matching_cdp_entry.get("neighbor")

                # Step 3: Find neighbor device ID
                neighbor_device = next(
                    (dev for dev in results if dev.get("prompt") == neighbor_name), None
                )

                if neighbor_device:
                    neighbor_id = neighbor_device.get("id")

                    # Step 4: Create link dictionary
                    link = {"from": device_id, "to": neighbor_id}
                    links_to_be_deleted.append(link)

    print("\nlinks_to_be_deleted: ", links_to_be_deleted)
    return links_to_be_deleted


results = [
    {
        "cdp_output_parsed": [
            {
                "capability": "R S I",
                "holdtime": "125",
                "local_interface": "G 0/0",
                "neighbor": "SW4",
                "neighbor_interface": "G 0/3",
                "platform": "",
            }
        ],
        "cdp_output_raw": "Capability Codes: R - Router, T - Trans Bridge, B - Source "
        "Route Bridge\n"
        "                  S - Switch, H - Host, I - IGMP, r - "
        "Repeater, P - Phone, \n"
        "                  D - Remote, C - CVTA, M - Two-port Mac "
        "Relay \n"
        "\n"
        "Device ID        Local Intrfce     Holdtme    Capability  "
        "Platform  Port ID\n"
        "SW4.jeremysitlab.com\n"
        "                 Gig 0/0           125             R S "
        "I            Gig 0/3\n"
        "\n"
        "Total cdp entries displayed : 1",
        "device": "192.168.150.135",
        "device_type": "cisco_ios",
        "id": 0,
        "label": "SW5",
        "level": 9999,
        "port": 22,
        "prompt": "SW5",
        "status": "success",
        "stp_output_parsed": [
            {
                "cost": "4",
                "interface": "G 0/0",
                "port_id": "1",
                "port_priority": "128",
                "role": "Root",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 0/1",
                "port_id": "2",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 0/2",
                "port_id": "3",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 0/3",
                "port_id": "4",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 1/0",
                "port_id": "5",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 1/1",
                "port_id": "6",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 1/2",
                "port_id": "7",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 1/3",
                "port_id": "8",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
        ],
        "stp_output_raw": "\n"
        "VLAN0001\n"
        "  Spanning tree enabled protocol rstp\n"
        "  Root ID    Priority    4097\n"
        "             Address     50a4.8500.0200\n"
        "             Cost        12\n"
        "             Port        1 (GigabitEthernet0/0)\n"
        "             Hello Time   2 sec  Max Age 20 sec  Forward "
        "Delay 15 sec\n"
        "\n"
        "  Bridge ID  Priority    32769  (priority 32768 sys-id-ext "
        "1)\n"
        "             Address     5003.0400.0f00\n"
        "             Hello Time   2 sec  Max Age 20 sec  Forward "
        "Delay 15 sec\n"
        "             Aging Time  300 sec\n"
        "\n"
        "Interface           Role Sts Cost      Prio.Nbr Type\n"
        "------------------- ---- --- --------- -------- "
        "--------------------------------\n"
        "Gi0/0               Root FWD 4         128.1    Shr \n"
        "Gi0/1               Desg FWD 4         128.2    Shr \n"
        "Gi0/2               Desg FWD 4         128.3    Shr \n"
        "Gi0/3               Desg FWD 4         128.4    Shr \n"
        "Gi1/0               Desg FWD 4         128.5    Shr \n"
        "Gi1/1               Desg FWD 4         128.6    Shr \n"
        "Gi1/2               Desg FWD 4         128.7    Shr \n"
        "Gi1/3               Desg FWD 4         128.8    Shr \n"
        "\n",
        "title": "192.168.150.135 - cisco_ios",
    },
    {
        "cdp_output_parsed": [
            {
                "capability": "R S I",
                "holdtime": "128",
                "local_interface": "G 1/1",
                "neighbor": "SW3",
                "neighbor_interface": "G 1/2",
                "platform": "",
            },
            {
                "capability": "R S I",
                "holdtime": "163",
                "local_interface": "G 0/3",
                "neighbor": "SW5",
                "neighbor_interface": "G 0/0",
                "platform": "",
            },
        ],
        "cdp_output_raw": "Capability Codes: R - Router, T - Trans Bridge, B - Source "
        "Route Bridge\n"
        "                  S - Switch, H - Host, I - IGMP, r - "
        "Repeater, P - Phone, \n"
        "                  D - Remote, C - CVTA, M - Two-port Mac "
        "Relay \n"
        "\n"
        "Device ID        Local Intrfce     Holdtme    Capability  "
        "Platform  Port ID\n"
        "SW3.jeremysitlab.com\n"
        "                 Gig 1/1           128             R S "
        "I            Gig 1/2\n"
        "SW5.jeremysitlab.com\n"
        "                 Gig 0/3           163             R S "
        "I            Gig 0/0\n"
        "\n"
        "Total cdp entries displayed : 2",
        "device": "192.168.150.134",
        "device_type": "cisco_ios",
        "id": 1,
        "label": "SW4",
        "level": 9999,
        "port": 22,
        "prompt": "SW4",
        "status": "success",
        "stp_output_parsed": [
            {
                "cost": "4",
                "interface": "G 0/0",
                "port_id": "1",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 0/1",
                "port_id": "2",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 0/2",
                "port_id": "3",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 0/3",
                "port_id": "4",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 1/0",
                "port_id": "5",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 1/1",
                "port_id": "6",
                "port_priority": "128",
                "role": "Root",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 1/2",
                "port_id": "7",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 1/3",
                "port_id": "8",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
        ],
        "stp_output_raw": "\n"
        "VLAN0001\n"
        "  Spanning tree enabled protocol rstp\n"
        "  Root ID    Priority    4097\n"
        "             Address     50a4.8500.0200\n"
        "             Cost        8\n"
        "             Port        6 (GigabitEthernet1/1)\n"
        "             Hello Time   2 sec  Max Age 20 sec  Forward "
        "Delay 15 sec\n"
        "\n"
        "  Bridge ID  Priority    32769  (priority 32768 sys-id-ext "
        "1)\n"
        "             Address     5026.1700.0e00\n"
        "             Hello Time   2 sec  Max Age 20 sec  Forward "
        "Delay 15 sec\n"
        "             Aging Time  300 sec\n"
        "\n"
        "Interface           Role Sts Cost      Prio.Nbr Type\n"
        "------------------- ---- --- --------- -------- "
        "--------------------------------\n"
        "Gi0/0               Desg FWD 4         128.1    Shr \n"
        "Gi0/1               Desg FWD 4         128.2    Shr \n"
        "Gi0/2               Desg FWD 4         128.3    Shr \n"
        "Gi0/3               Desg FWD 4         128.4    Shr \n"
        "Gi1/0               Desg FWD 4         128.5    Shr \n"
        "Gi1/1               Root FWD 4         128.6    Shr \n"
        "Gi1/2               Desg FWD 4         128.7    Shr \n"
        "Gi1/3               Desg FWD 4         128.8    Shr \n"
        "\n",
        "title": "192.168.150.134 - cisco_ios",
    },
    {
        "cdp_output_parsed": [
            {
                "capability": "R S I",
                "holdtime": "174",
                "local_interface": "G 0/0",
                "neighbor": "SW1",
                "neighbor_interface": "G 0/2",
                "platform": "",
            },
            {
                "capability": "R S I",
                "holdtime": "173",
                "local_interface": "G 1/0",
                "neighbor": "SW2",
                "neighbor_interface": "G 0/1",
                "platform": "",
            },
            {
                "capability": "R S I",
                "holdtime": "170",
                "local_interface": "G 1/2",
                "neighbor": "SW4",
                "neighbor_interface": "G 1/1",
                "platform": "",
            },
        ],
        "cdp_output_raw": "Capability Codes: R - Router, T - Trans Bridge, B - Source "
        "Route Bridge\n"
        "                  S - Switch, H - Host, I - IGMP, r - "
        "Repeater, P - Phone, \n"
        "                  D - Remote, C - CVTA, M - Two-port Mac "
        "Relay \n"
        "\n"
        "Device ID        Local Intrfce     Holdtme    Capability  "
        "Platform  Port ID\n"
        "SW1.jeremysitlab.com\n"
        "                 Gig 0/0           174             R S "
        "I            Gig 0/2\n"
        "SW2.jeremysitlab.com\n"
        "                 Gig 1/0           173             R S "
        "I            Gig 0/1\n"
        "SW4.jeremysitlab.com\n"
        "                 Gig 1/2           170             R S "
        "I            Gig 1/1\n"
        "\n"
        "Total cdp entries displayed : 3",
        "device": "192.168.150.133",
        "device_type": "cisco_ios",
        "id": 2,
        "label": "SW3",
        "level": 9999,
        "port": 22,
        "prompt": "SW3",
        "status": "success",
        "stp_output_parsed": [
            {
                "cost": "4",
                "interface": "G 0/0",
                "port_id": "1",
                "port_priority": "128",
                "role": "Altn",
                "status": "BLK",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 0/1",
                "port_id": "2",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 0/2",
                "port_id": "3",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 0/3",
                "port_id": "4",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 1/0",
                "port_id": "5",
                "port_priority": "128",
                "role": "Root",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 1/1",
                "port_id": "6",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 1/2",
                "port_id": "7",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 1/3",
                "port_id": "8",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
        ],
        "stp_output_raw": "\n"
        "VLAN0001\n"
        "  Spanning tree enabled protocol rstp\n"
        "  Root ID    Priority    4097\n"
        "             Address     50a4.8500.0200\n"
        "             Cost        4\n"
        "             Port        5 (GigabitEthernet1/0)\n"
        "             Hello Time   2 sec  Max Age 20 sec  Forward "
        "Delay 15 sec\n"
        "\n"
        "  Bridge ID  Priority    32769  (priority 32768 sys-id-ext "
        "1)\n"
        "             Address     50e6.1c00.0d00\n"
        "             Hello Time   2 sec  Max Age 20 sec  Forward "
        "Delay 15 sec\n"
        "             Aging Time  300 sec\n"
        "\n"
        "Interface           Role Sts Cost      Prio.Nbr Type\n"
        "------------------- ---- --- --------- -------- "
        "--------------------------------\n"
        "Gi0/0               Altn BLK 4         128.1    Shr \n"
        "Gi0/1               Desg FWD 4         128.2    Shr \n"
        "Gi0/2               Desg FWD 4         128.3    Shr \n"
        "Gi0/3               Desg FWD 4         128.4    Shr \n"
        "Gi1/0               Root FWD 4         128.5    Shr \n"
        "Gi1/1               Desg FWD 4         128.6    Shr \n"
        "Gi1/2               Desg FWD 4         128.7    Shr \n"
        "Gi1/3               Desg FWD 4         128.8    Shr \n"
        "\n",
        "title": "192.168.150.133 - cisco_ios",
    },
    {
        "cdp_output_parsed": [
            {
                "capability": "R S I",
                "holdtime": "150",
                "local_interface": "G 0/0",
                "neighbor": "SW1",
                "neighbor_interface": "G 0/1",
                "platform": "",
            },
            {
                "capability": "R S I",
                "holdtime": "177",
                "local_interface": "G 0/1",
                "neighbor": "SW3",
                "neighbor_interface": "G 1/0",
                "platform": "",
            },
        ],
        "cdp_output_raw": "Capability Codes: R - Router, T - Trans Bridge, B - Source "
        "Route Bridge\n"
        "                  S - Switch, H - Host, I - IGMP, r - "
        "Repeater, P - Phone, \n"
        "                  D - Remote, C - CVTA, M - Two-port Mac "
        "Relay \n"
        "\n"
        "Device ID        Local Intrfce     Holdtme    Capability  "
        "Platform  Port ID\n"
        "SW1.jeremysitlab.com\n"
        "                 Gig 0/0           150             R S "
        "I            Gig 0/1\n"
        "SW3.jeremysitlab.com\n"
        "                 Gig 0/1           177             R S "
        "I            Gig 1/0\n"
        "\n"
        "Total cdp entries displayed : 2",
        "device": "192.168.150.132",
        "device_type": "cisco_ios",
        "id": 3,
        "label": "SW2",
        "level": 9999,
        "port": 22,
        "prompt": "SW2",
        "status": "success",
        "stp_output_parsed": [
            {
                "cost": "4",
                "interface": "G 0/0",
                "port_id": "1",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 0/1",
                "port_id": "2",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 0/2",
                "port_id": "3",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 0/3",
                "port_id": "4",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 1/0",
                "port_id": "5",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 1/1",
                "port_id": "6",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 1/2",
                "port_id": "7",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 1/3",
                "port_id": "8",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
        ],
        "stp_output_raw": "\n"
        "VLAN0001\n"
        "  Spanning tree enabled protocol rstp\n"
        "  Root ID    Priority    4097\n"
        "             Address     50a4.8500.0200\n"
        "             This bridge is the root\n"
        "             Hello Time   2 sec  Max Age 20 sec  Forward "
        "Delay 15 sec\n"
        "\n"
        "  Bridge ID  Priority    4097   (priority 4096 sys-id-ext "
        "1)\n"
        "             Address     50a4.8500.0200\n"
        "             Hello Time   2 sec  Max Age 20 sec  Forward "
        "Delay 15 sec\n"
        "             Aging Time  300 sec\n"
        "\n"
        "Interface           Role Sts Cost      Prio.Nbr Type\n"
        "------------------- ---- --- --------- -------- "
        "--------------------------------\n"
        "Gi0/0               Desg FWD 4         128.1    Shr \n"
        "Gi0/1               Desg FWD 4         128.2    Shr \n"
        "Gi0/2               Desg FWD 4         128.3    Shr \n"
        "Gi0/3               Desg FWD 4         128.4    Shr \n"
        "Gi1/0               Desg FWD 4         128.5    Shr \n"
        "Gi1/1               Desg FWD 4         128.6    Shr \n"
        "Gi1/2               Desg FWD 4         128.7    Shr \n"
        "Gi1/3               Desg FWD 4         128.8    Shr \n"
        "\n",
        "title": "192.168.150.132 - cisco_ios",
    },
    {
        "cdp_output_parsed": [
            {
                "capability": "R S I",
                "holdtime": "179",
                "local_interface": "G 0/1",
                "neighbor": "SW2",
                "neighbor_interface": "G 0/0",
                "platform": "",
            },
            {
                "capability": "R S I",
                "holdtime": "160",
                "local_interface": "G 0/2",
                "neighbor": "SW3",
                "neighbor_interface": "G 0/0",
                "platform": "",
            },
        ],
        "cdp_output_raw": "Capability Codes: R - Router, T - Trans Bridge, B - Source "
        "Route Bridge\n"
        "                  S - Switch, H - Host, I - IGMP, r - "
        "Repeater, P - Phone, \n"
        "                  D - Remote, C - CVTA, M - Two-port Mac "
        "Relay \n"
        "\n"
        "Device ID        Local Intrfce     Holdtme    Capability  "
        "Platform  Port ID\n"
        "SW2.jeremysitlab.com\n"
        "                 Gig 0/1           179             R S "
        "I            Gig 0/0\n"
        "SW3.jeremysitlab.com\n"
        "                 Gig 0/2           160             R S "
        "I            Gig 0/0\n"
        "\n"
        "Total cdp entries displayed : 2",
        "device": "192.168.150.131",
        "device_type": "cisco_ios",
        "id": 4,
        "label": "SW1",
        "level": 9999,
        "port": 22,
        "prompt": "SW1",
        "status": "success",
        "stp_output_parsed": [
            {
                "cost": "4",
                "interface": "G 0/0",
                "port_id": "1",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 0/1",
                "port_id": "2",
                "port_priority": "128",
                "role": "Root",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 0/2",
                "port_id": "3",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 0/3",
                "port_id": "4",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 1/0",
                "port_id": "5",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 1/1",
                "port_id": "6",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 1/2",
                "port_id": "7",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
            {
                "cost": "4",
                "interface": "G 1/3",
                "port_id": "8",
                "port_priority": "128",
                "role": "Desg",
                "status": "FWD",
                "type": "Shr ",
                "vlan_id": "1",
            },
        ],
        "stp_output_raw": "\n"
        "VLAN0001\n"
        "  Spanning tree enabled protocol rstp\n"
        "  Root ID    Priority    4097\n"
        "             Address     50a4.8500.0200\n"
        "             Cost        4\n"
        "             Port        2 (GigabitEthernet0/1)\n"
        "             Hello Time   2 sec  Max Age 20 sec  Forward "
        "Delay 15 sec\n"
        "\n"
        "  Bridge ID  Priority    32769  (priority 32768 sys-id-ext "
        "1)\n"
        "             Address     50be.3500.0100\n"
        "             Hello Time   2 sec  Max Age 20 sec  Forward "
        "Delay 15 sec\n"
        "             Aging Time  300 sec\n"
        "\n"
        "Interface           Role Sts Cost      Prio.Nbr Type\n"
        "------------------- ---- --- --------- -------- "
        "--------------------------------\n"
        "Gi0/0               Desg FWD 4         128.1    Shr \n"
        "Gi0/1               Root FWD 4         128.2    Shr \n"
        "Gi0/2               Desg FWD 4         128.3    Shr \n"
        "Gi0/3               Desg FWD 4         128.4    Shr \n"
        "Gi1/0               Desg FWD 4         128.5    Shr \n"
        "Gi1/1               Desg FWD 4         128.6    Shr \n"
        "Gi1/2               Desg FWD 4         128.7    Shr \n"
        "Gi1/3               Desg FWD 4         128.8    Shr \n"
        "\n",
        "title": "192.168.150.131 - cisco_ios",
    },
]

identify_blocked_links(results)
