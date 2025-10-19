![](https://img.shields.io/badge/python-3.8+-blue.svg)
![](https://img.shields.io/badge/Ubuntu-20.04-orange.svg)
# Clusternet

This project extends the [Containernet](https://github.com/containernet/containernet) emulation environment to span the emulation across several physical machines.

## Dependencies
- [Containernet](https://github.com/containernet/containernet) (Use the Option 1 installation)
## Install

```
sudo pip install -U git+https://github.com/EsauM10/clusternet.git
```

## Usage
Run a Worker in a machine with:
```
sudo RunWorker -p=5000
```
Choose a machine to run an Openflow Controller with:
```
controller -v ptcp=6633
```
And then, create a topoly and save to a file.
```python
from clusternet.client import RemoteWorker

worker = RemoteWorker(ip='192.168.0.152', port=5000)

try:
    worker.add_controller('c0', ip='192.168.0.152', port=6633)
    worker.add_switch('s1')
    d1 = worker.add_docker(name='d1', ip='10.0.0.1', dimage='ubuntu:trusty')
    d2 = worker.add_docker(name='d2', ip='10.0.0.2', dimage='ubuntu:trusty')

    worker.add_link('d1', 's1')
    worker.add_link('d2', 's1')

    worker.start()
    worker.run_pingall()
    
    print(d1.cmd('ifconfig'))
    print(d2.cmd(f'ping -c 4 {d1.get_ip()}'))

except Exception as ex:
    print(ex)
finally:
    worker.stop()
```
This example runs one worker and the Openflow Controller in the same machine, make sure the IP addresses and ports are configured correctly and run it with:
```
sudo python3 topology.py
```
