# pyAtmoWeb 
### Disclaimer
This software is an independent product and is not developed, maintained, or endorsed by Memmert. All trademarks, brand names, and product names referenced in this software are the property of their respective owners.

This software is designed to interface with machines manufactured by Memmert, but it is not affiliated with, authorized by, or supported byMemmert in any way. Use of this software is at the user's own risk. The developers of this software make no warranties, express or implied, regarding compatibility, functionality, or reliability when used in conjunction with Memmert’s hardware or software.

By using this software, you acknowledge that Memmert is not responsible for any damage, malfunction, or loss resulting from its use.

### Introduction:
The module was developed for use at IPF Dresden as a tool to extract data via REST from
ovens manufactured by Memmert. The python module implements the Memmert REST API *AtmoWeb*.
The here published module was tested with a Memmert UF55 plus oven.<p>
Before working with this software please refer to the AtmoWeb documentation of the REST interface from Memmert at:

- https://www.memmert.com/de/downloads/downloads/software/#!filters=%7B%7D
- https://www.memmert.com/index.php?eID=dumpFile&t=f&f=5708&token=e46b35fe2d26d6e83f1db73c13c9314db165a9f0

An uptodate version of the module documented in this readme can be found at the following IPF GitLab repository:<p>
- https://gitlab.ipfdd.de/Henn/pyatmoweb

If you encounter problems while using this software or have ideas for enhancing it, please feel free 
to contribute to this GitLab repository or get in contact with the auther at henn@ipfdd.de!

### Setup:

#### Networkconfiguration:
To establish a connection the oven needs to be connected via Ethernet to the computer running the software.
The ethernet adapter of the computer needs to be configured for IPv4 without DHCP / static ip addresses.

1) Find out the IP address and subnet mask of the oven. You can find it inside the "Settings" menu at the oven itself.
It might be somthing like: <p>"192.168.100.100" / "255.255.0.0"


2) Navigate to the IPv4 settings of the network adapter on your computer and configure it like in the following example:<p>
**IP:         192.168.5.2**<p>
**Gateway:    192.168.5.1**<p>
**Subnet:     255.255.0.0**<p>
**leave DHCP empty**

Please ashore a working connection before using the module!
A connection to the oven can be verified by trying to ping the ip address of the oven.

#### Python:
To work with the module use Python 3.10 or newer. The module relies on the following packages that can be installed
using pip.
- requests
- json
- logging

Locate the pyAtmoWeb.py file in the root folder of your python script.
Use the module as in the following:<p>

```
import time
import pyAtmoWeb as paw

ip_address = "192.168.100.100"

for i in range(0, 9):
    print(paw.get_temp_1(ip_address))
    time.sleep(1)
```

### Licence
The module is published under MIT Licence: 


>MIT License
>
>Copyright (c) 2024 Enno Henn, Leibniz Institute of Polymer Research Dresden
>
>Permission is hereby granted, free of charge, to any person obtaining a copy
>of this software and associated documentation files (the "Software"), to deal
>in the Software without restriction, including without limitation the rights
>to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
>copies of the Software, and to permit persons to whom the Software is
>furnished to do so, subject to the following conditions:
>
>The above copyright notice and this permission notice shall be included in all
>copies or substantial portions of the Software.
>
>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
>IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
>FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL THE
>AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
>LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
>OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
>SOFTWARE.
