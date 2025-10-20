# BloxAPI

**Powerful and versatile Python3 wrapper for ROBLOX Web API**

## Installation

```bash
pip install bloxypy
```

## Information

Welcome, and thank you for using BloxAPI!
BloxAPI is an object oriented, asynchronous wrapper for the Roblox Web API (and other Roblox-related APIs) with many new and interesting features.
BloxAPI allows you to automate much of what you would do on the Roblox website and on other Roblox-related websites.

## Get Started

To begin, first import and setup the client, which is the most essential part of BloxAPI, and initialize it like so:

```python
from bloxapi import Client

# Create client instance
client = Client()

# Example 1: Get asset information
print("Getting asset information...")
asset_result = client.get_asset(123456)  # Replace with a valid asset ID
print(f"Asset result: {asset_result}")

# Example 2: Get user information
print("\nGetting user information...")
user_result = client.get_user(1)  # Roblox user ID 1 (roblox)
print(f"User result: {user_result}")
```

# Disclaimer
We are not responsible for any malicious use of this library.
If you use this library in a way that violates the Roblox Terms of Use your account may be punished.
If you use code from BloxAPI in your own library, please credit us! We're working our hardest to deliver this library, and crediting us is the best way to help support the project.

# Documentation
You can view documentation for BloxAPI at bloxapi.jmksite.dev.
If something's missing from docs, feel free to dive into the code and read the docstrings as most things are documented there. The docs are generated from docstrings in the code using pdoc3.

# Installation
You can install BloxAPI from pip
```
pip3 install ro.py
```