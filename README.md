## Spanning tree protocol (STP)


## Pre-configuration process

I have created an automated process to configure multiple network switches using a Python 3 script. 

Using PNETLab, each device can be accessed via Telnet from a default port range of 30001.

This allows us to send a set of commands to each device in the lab. You just need to complete the *credentials.json* file available in the directory sand execute the mentioned script.

What we are avoiding here is the process of creating one txt file per each network switch and avoiding to manually have to modify values inside each txt file. 

Tested on 5 devices resulting in a execution time of approximately 2 seconds.

Image name used is available in the readme file of the [directory](https://github.com/mvarrone/stp-project/tree/master/backend/automate_config).

