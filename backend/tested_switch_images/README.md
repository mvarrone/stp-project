# Tested images

## Server information

- VMware® Workstation 17 Pro - *Version: 17.5.2 build-23775571*
- Linux pnetlab 4.15.18-pnetlab2 #1 SMP Sun Jan 31 20:04:56 UTC 2021 x86_64 x86_64 x86_64 GNU/Linux
- PNETLab v4.2.10
- ishare2: 3.5.4-main

## List of tested images

|  #  | Image name                                      | Working? | Description                                                   | *ishare2* command     |
| :-: | :---------------------------------------------: | :------: | :-----------------------------------------------------------: | :-------------------: |             
|  1  | vios-15.5.3M                                    |   No     | No *interface vlan 1* command available                       | ishare2 pull qemu 918 |
|  2  | viosl2-adventerpriseK9-M_152_May_2018           |   No     | Problem with STP interface Role/Status                        | ishare2 pull qemu 931 |
|  3  | viosl2-adventerprisek9-m.ssa.high_iron_20190423 |   No     | Booting constantly. It crashes after a while                  | ishare2 pull qemu 935 |
|  4  | viosl2-15.2.4.55e                               |   Yes    | It seems to be working fine. I am going to keep working on it | ishare2 pull qemu 930 |
