# SnakeScan
![PyPI version](https://badge.fury.io/py/SnakeScan.svg)
![Requires-python](https://img.shields.io/badge/requires--python-3.6+-red)
![License](https://img.shields.io/badge/License-MIT-blue.svg)
 ```
import SnakeScan
SnakeScan.run()
```
## Help

- --l  need internet to view public ip you device
- --t threading port search
- --d dos
- --s single port search
- --i information about host
- --h in host /--h port in host

## Added class Watcher:
     ```
     for SnakeScan import Watcher
     Watcher(host:str,port:int)
     ``` 
## Added more imformation about host:
    ```
   [$]Host-->www.example.com --i
   Type IP: <class 'ipaddress.IPv4Address'>
   Version IP: 4
   Network: 2.21.240.0/24
   Subnet mask: 255.255.255.0
   Host:a2-21-240-137.deploy.static
   akamaitechnologies.com
   IP:2.21.240.137
```