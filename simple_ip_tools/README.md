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
import simple_ip_tools

simple_ip_tools.gen_db_from_maxmind_csv("ipdb.bin")
ipdb = simple_ip_tools.load_db("ipdb.bin")
simple_ip_tools.lookup_db(ipdb, "1.2.3.4")
simple_ip_tools.lookup_db(ipdb, "2a01:cb06:c200:3e51:103d:6143:42e0:3d48")
```

## Contributing
1. Fork the repo  
2. Create a feature branch (`git checkout -b feature/foo`)  
3. Commit your changes (`git commit -am 'Add foo feature'`)  
4. Push to the branch (`git push origin feature/foo`)  
5. Open a pull request

## License
MIT License – see [LICENSE](LICENSE) for details.
