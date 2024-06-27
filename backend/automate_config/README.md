# Automate switch configs

## Requirements

- Python 3.12.2
- telnetlib3 2.0.4
- PNETLab 4.2.10
- Switch image: [viosl2-15.2.4.55e](https://github.com/mvarrone/stp-project/tree/master/backend/tested_switch_images). Number 4 in the table

## Description

Script designed to Telnet multiple network switches using a template (set of commands) and a *credentials.json* file in order to configure them at once. After this process, each network switch will result in having SSH v2 enabled. 

It is recommended to use SSH v2 for security reasons and for being able to execute some commands related to gathering spanning tree protocol data in a better manner (obtain parsed data from each device)

## Tests

Tested on 5 devices resulting in a execution time of approximately 2 seconds.