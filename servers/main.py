#!/usr/bin/env python3

import logging
import os
from functools import cache
from typing import Type

import napalm
import yaml
from mcp.server.fastmcp import FastMCP
from napalm.base.base import NetworkDriver
from toon_format import encode

logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("napalm-geminicli-extension")

# Get inventory filename
_inventory_filename = os.getenv("GEMINI_CLI_NAPALM_INVENTORY_FILENAME") or "inventory.yaml"
if os.path.isabs(_inventory_filename):
    INVENTORY_FILE = _inventory_filename
else:
    INVENTORY_FILE = os.path.join(os.path.dirname(__file__), _inventory_filename)


@cache
def get_inventory_data(hostname: str) -> tuple[Type[NetworkDriver], str, str]:
    """Get the driver for the device."""

    # Load inventory file
    if not os.path.exists(INVENTORY_FILE):
        raise FileNotFoundError(
            f"Inventory file not found at: {INVENTORY_FILE}. Absolute path: {os.path.abspath(INVENTORY_FILE)}"
        )
    with open(INVENTORY_FILE, "r") as fh:
        inventory = yaml.safe_load(fh)

    try:
        device = inventory[hostname]
    except KeyError:
        logger.error(f"Device {hostname} not found in inventory")
        raise ValueError("Device not found in inventory.")

    driver = device["driver"]
    username = device["username"]
    password = device["password"]

    return napalm.get_network_driver(driver), username, password


def execute_device_method(hostname: str, method_name: str, *args) -> dict:
    """Execute a method on a NAPALM device and return encoded results."""
    driver, username, password = get_inventory_data(hostname)

    with driver(hostname, username, password) as device:
        method = getattr(device, method_name)
        data = method(*args) if args else method()
        return encode(data)


@mcp.tool()
async def get_device_os(hostname: str) -> dict:
    """Return the device OS."""

    # Load inventory file
    if not os.path.exists(INVENTORY_FILE):
        raise FileNotFoundError(
            f"Inventory file not found at: {INVENTORY_FILE}. Absolute path: {os.path.abspath(INVENTORY_FILE)}"
        )
    with open(INVENTORY_FILE, "r") as fh:
        inventory = yaml.safe_load(fh)

    try:
        device = inventory[hostname]
    except KeyError:
        logger.error(f"Device {hostname} not found in inventory")
        raise ValueError("Device not found in inventory.")

    return device["driver"]


@mcp.tool()
async def traceroute(hostname: str, destination: str) -> dict:
    """Traceroute to an IP address from the device."""
    return execute_device_method(hostname, "traceroute", destination)


@mcp.tool()
async def ping(hostname: str, destination: str) -> dict:
    """Ping an IP address from the device."""
    return execute_device_method(hostname, "ping", destination)


@mcp.tool()
async def get_bgp_neighbors(hostname: str) -> dict:
    """Get BGP neighbors on the given device."""
    return execute_device_method(hostname, "get_bgp_neighbors")


@mcp.tool()
async def get_facts(hostname: str) -> dict:
    """Get device facts."""
    return execute_device_method(hostname, "get_facts")


@mcp.tool()
async def get_interfaces(hostname: str) -> dict:
    """Get interface details for the given device."""
    return execute_device_method(hostname, "get_interfaces")


@mcp.tool()
async def get_interfaces_ip(hostname: str) -> dict:
    """Get interface IP addresses for the given device."""
    return execute_device_method(hostname, "get_interfaces_ip")


@mcp.tool()
async def get_lldp_neighbors(hostname: str) -> dict:
    """Get the LLDP neighbors from the device."""
    return execute_device_method(hostname, "get_lldp_neighbors")


@mcp.tool()
async def run_command(hostname: str, command: str) -> dict:
    """Run command on the device and return the output. The command needs to be native to the device OS."""

    driver, username, password = get_inventory_data(hostname)

    with driver(hostname, username, password) as device:
        data = device.cli([command])

    if data:
        return encode(data)

    return data


if __name__ == "__main__":
    logger.info("Starting NAPALM GeminiCLI Extension…")
    mcp.run()
