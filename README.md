# NAPALM GeminiCLI extension

A Gemini CLI extension that uses NAPALM to get configuration and operational data from network devices.

## Setup

Install the extention using gemini:

```
gemini extensions install https://github.com/stiltzkin10/napalm-geminicli-extension
```

Create an inventory file `inventory.yaml` file which specifies the NAPALM driver/username/password to use for each device. See `servers/inventory.yaml` for an example.

Export the inventory file path and start Gemini CLI:

```
export GEMINI_CLI_NAPALM_INVENTORY_FILENAME=/path_to_inventory/inventory.yaml
gemini
```

That's it! Start gemini and play around =)

## Example prompts

* Save the running config from arista1 to a local file arista1_running_config.txt
* How many NTP server are configured on arista1?
* Get the ARP table from arista1
* Is there IPv6 connectivity between arista1 and juniper1?