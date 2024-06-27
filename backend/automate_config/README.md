# Automate switch configs

## Requirements

- Python 3.12.2
- telnetlib3 2.0.4
- PNETLab 4.2.10
- Switch image: [viosl2-15.2.4.55e](https://github.com/mvarrone/stp-project/tree/master/backend/tested_switch_images). Number 4 in the table

## Description

Script designed to Telnet multiple network switches using a template (set of commands) and a *credentials.json* file in order to configure them at once. After this process, each network switch will result in having SSH v2 enabled. 

It is recommended to use SSH v2 for security reasons and for being able to execute some commands related to gathering spanning tree protocol data in a better manner (obtain parsed data from each device)

In a real world environment, devices already have SSH v2 enabled and there would be no need to execute this scritpt. Also, Telnet for sure would not be enabled.

So, the purpose of this script is to be used mainly in a lab environment where devices start with no configuration (no ssh v2) and with Telnet enabled. 

## Tests

- Tested on 5 devices resulting in a execution time of approximately 2 seconds.

- Tested on 6 devices resulting in a execution time of approximately 2 seconds as well: In this case, we created a new dictionary in *credentials.json* file containing a new switch not created in the lab.