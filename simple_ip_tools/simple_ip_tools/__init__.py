"""
simple_ip_tools
===============
This module provides utilities for validating IP addresses, determining their version,
and building, loading, and querying an IP‑to‑country database based on MaxMind CSV
datasets and PyTricia prefix trees.
    IPV4    (int): Represents the IPv4 address version.
    IPV6    (int): Represents the IPv6 address version.
Args:
    address (str): The IP address string to validate.
Returns:
    bool: True if the address is a valid IPv4 or IPv6 address; False otherwise.
Returns IPVersion.IPV4 or IPVersion.IPV6 if the given string is a valid IP address,
Args:
    address (str): The IP address string whose version is to be determined.
Returns:
    IPVersion: The detected IP version, or UNKNOWN if invalid.
Args:
    db_path   (str): Filepath to save the pickled database.
    geo_csv   (str): Path to the geoname‑country CSV file.
    ipv4_csv  (str): Path to the IPv4 network‑to‑country CSV file.
    ipv6_csv  (str): Path to the IPv6 network‑to‑country CSV file.
Returns:
    bool: True on successful database generation; False on failure.
Load the pickled IP‑to‑country mapping database.
Args:
    db_path (str): Filepath of the pickled database to load.
Returns:
    dict[IPVersion, pytricia.PyTricia]: A mapping from IP versions to PyTricia
    prefix trees containing network‑to‑country mappings.
Args:
    db (dict[IPVersion, pytricia.PyTricia]): Loaded database mapping versions to PyTricia trees.
    ip (str): The IP address to look up.
Returns:
    str | None: The country ISO code if found, "Private" for private IP ranges,
    or None if the address is invalid or not in the database.
Args:
    csv_path (str): Path to the geoname‑country CSV file.
Returns:
    dict[int, str]: A mapping from geoname IDs to country ISO codes.
Args:
    csv_path (str): Path to the network‑to‑registered‑country CSV file.
Returns:
    dict[str, Optional[int]]: A mapping from network CIDR strings to geoname IDs,
    or None for networks without a registered country.

"""

from enum import Enum
import ipaddress
import pickle
import csv
import pytricia
from dataclasses import dataclass
from typing import Optional

__version__ = "0.2.1"


@dataclass
class CountryOnly:
    """
    Represents a country with its ISO code."""

    country_iso_code: str


@dataclass
class CountryCity:
    """
    Represents a country and city with their ISO codes."""

    country_iso_code: str
    city_name: str


@dataclass
class Private:
    """
    Represents a private IP address."""

    pass


GeoLocation = CountryOnly | CountryCity | Private


class IPVersion(Enum):
    """
    Enumeration of IP address versions.
    Attributes:
        UNKNOWN (int): Represents an unrecognized or invalid IP version.
        IPv4    (int): Represents the IPv4 address version.
        IPv6    (int): Represents the IPv6 address version.
    """

    UNKNOWN = 0
    IPV4 = 4
    IPV6 = 6


def is_valid_ip(address: str) -> bool:
    """
    Check whether a given string is a valid IPv4 or IPv6 address.
    """

    try:
        ipaddress.ip_address(address)
        return True
    except ValueError:
        return False


def get_ip_version(address: str) -> IPVersion:
    """
    Returns IPVersion.IPv4 or IPVersion.IPv6 if the given string is a valid IP address,
    otherwise returns IPVersion.UNKNOWN.
    """

    try:
        ip = ipaddress.ip_address(address)
        return (
            IPVersion.IPV4 if isinstance(ip, ipaddress.IPv4Address) else IPVersion.IPV6
        )
    except ValueError:
        return IPVersion.UNKNOWN


def gen_db_from_maxmind_csv(
    db_path: str,
    geo_csv: str = "GeoIP2-Country-Locations-en.csv",
    ipv4_csv: str = "GeoIP2-Country-Blocks-IPv4.csv",
    ipv6_csv: str = "GeoIP2-Country-Blocks-IPv6.csv",
) -> bool:
    """
    Generates a mapping of IP networks to country ISO codes using MaxMind CSV datasets.
    """

    geo_map = __load_geoname_country_map(geo_csv)
    ipv4_map = __load_network_to_registered_country(ipv4_csv)
    ipv6_map = __load_network_to_registered_country(ipv6_csv)

    def _map_networks(ip_map):
        pairs = []
        for network, reg_id in ip_map.items():
            if reg_id is None:
                continue
            country = geo_map.get(reg_id)
            if country:
                pairs.append((network, country))
            else:
                return None
        return pairs

    ptv4 = _map_networks(ipv4_map)
    if ptv4 is None:
        return False

    ptv6 = _map_networks(ipv6_map)
    if ptv6 is None:
        return False

    db = {IPVersion.IPV4: ptv4, IPVersion.IPV6: ptv6}

    with open(db_path, "wb") as f:
        pickle.dump(db, f)
        return True

    return False


def load_db(db_path: str) -> dict[IPVersion, pytricia.PyTricia]:
    """
    Load the pickled IP-to-country mapping database.
    """

    with open(db_path, "rb") as f:
        db = pickle.load(f)

        ptv6 = pytricia.PyTricia(128)
        for network, country in db[IPVersion.IPV6]:
            ptv6.insert(network, country)

        ptv4 = pytricia.PyTricia(32)
        for network, country in db[IPVersion.IPV4]:
            ptv4.insert(network, country)

        return {IPVersion.IPV4: ptv4, IPVersion.IPV6: ptv6}


def lookup_db(db: dict[IPVersion, pytricia.PyTricia], ip: str) -> GeoLocation | None:
    """
    Lookup the country ISO code for a given IP address using the loaded database.
    """

    version = get_ip_version(ip)
    if version == IPVersion.UNKNOWN:
        return None

    ptv = db.get(version)
    if ptv is None:
        return None

    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private:
            return Private()
        return ptv[ip]
    except KeyError:
        # IP not found in the database and is not private
        return None
    except ValueError:
        # Should not happen if get_ip_version worked, but handle defensively
        return None


def __load_geoname_country_map(csv_path: str) -> dict[int, GeoLocation]:
    """
    Extracts geoname_id and country_iso_code from the CSV file
    and returns a dict mapping geoname_id to country_iso_code.
    """
    mapping = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "city_name" in reader.fieldnames:
            for row in reader:
                gid = int(row["geoname_id"])
                iso = row["country_iso_code"].strip()
                city = row["city_name"].strip()
                mapping[gid] = CountryCity(country_iso_code=iso, city_name=city)
        else:
            for row in reader:
                gid = int(row["geoname_id"])
                iso = row["country_iso_code"].strip()
                mapping[gid] = CountryOnly(country_iso_code=iso)
    return mapping


def __load_network_to_registered_country(csv_path: str) -> dict[str, Optional[int]]:
    """
    Extracts the network and registered_country_geoname_id columns from the CSV
    and returns a dict mapping network to registered_country_geoname_id.
    """
    mapping = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            network = row["network"].strip()
            reg_id = row["geoname_id"].strip()
            mapping[network] = int(reg_id) if reg_id else None
    return mapping
