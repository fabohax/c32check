# c32check

## Overview

`c32check` is a pure Python library for encoding and decoding [Stacks blockchain](https://www.stacks.co) addresses using the C32Check format. It also provides utilities for converting between Bitcoin Base58Check and Stacks addresses, mimicking the behavior of the original JavaScript [library](https://github.com/stacks-network/c32check) used by the Stacks ecosystem.

## Features

- Encode/decode C32Check addresses (used by Stacks)
- Convert Base58Check (Bitcoin) → C32Check (Stacks)
- Convert C32Check (Stacks) → Base58Check (Bitcoin)
- Validate checksum and address structure
- Fully compatible with Python 3.7+

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/fabohax/c32check.git
   ```

2. Navigate to the project directory:

   ```bash
   cd c32check
   ```

3. (Optional) Set up a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install in editable mode:

   ```bash
   pip install -e .
   ```

## Usage

```python
from c32check import c32address, b58_to_c32, c32_to_b58

# Generate a Stacks address (mainnet)
hash160 = '751e76e8199196d454941c45d1b3a323f1433bd6'
stx_address = c32address(22, hash160)
print(stx_address)  # e.g., SP2...

# Convert a BTC address to STX
btc_address = '1BoatSLRHtKNngkdXEeobR76b53LETtpyT'
converted = b58_to_c32(btc_address)
print(converted)

# Convert back from STX to BTC
btc_back = c32_to_b58(converted)
print(btc_back)
```

## Contributing

Contributions are welcome! Fork the repository and submit a pull request. Feel free to open issues or suggest improvements.

OSS 2025 🄯 Fabo Hax
