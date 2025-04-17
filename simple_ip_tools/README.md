# simple_ip_tools

A small Python library for managing IP networks using the standard `ipaddress` module and efficient prefix lookups with `pytricia`.

## Features
- Add, remove, and list IPv4/IPv6 networks
- Fast longest‑prefix match queries
- Simple, lightweight API

## Requirements
- Python 3.6+
- pytricia
- ipaddress (built‑in on Python ≥3.3; installed via requirements for older versions)

## Installation
```bash
pip install -r requirements.txt
```
_or for local development:_
```bash
pip install -e .
```

## Usage
```python
from simple_ip_tools import NetworkStore

# create a store and add networks
store = NetworkStore()
store.add_network("192.168.0.0/24", "Office LAN")
store.add_network("10.0.0.0/8", "Data Center")

# lookup an IP address
owner = store.lookup("192.168.0.42")
print(owner)  # outputs: Office LAN
```

## Contributing
1. Fork the repo  
2. Create a feature branch (`git checkout -b feature/foo`)  
3. Commit your changes (`git commit -am 'Add foo feature'`)  
4. Push to the branch (`git push origin feature/foo`)  
5. Open a pull request

## License
MIT License – see [LICENSE](LICENSE) for details.
