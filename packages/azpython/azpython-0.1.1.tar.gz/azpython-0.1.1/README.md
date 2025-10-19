# azpython
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

Official Python3 API connector for AZ.COM's HTTP APIs.

## Table of Contents

- [About](#about)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Contact](#contact)

## About
Put simply, `azpython` (Python + AZ.COM) is the official lightweight one-stop-shop module for the AZ.COM HTTP APIs. 

## Installation
`azpython` requires Python 3.9.1 or higher. The module can be installed manually or via [PyPI](https://pypi.org/project/azpython/) with `pip`:
```
pip install azpython
```

## Usage
You can retrieve a specific spot market like so:
```python
from azpython.spot import Spot
```

Create an HTTP session and connect via WebSocket for Inverse on mainnet:
```python
az = Spot(host="https://s-api.myaztests.com", access_key='', secret_key='')
```

Information can be sent to, or retrieved from, the AZ.COM APIs:
```python
print(az.balance("usdt"))
```

You can retrieve a specific future market like so:
```python
from azpython.perp import Perp
```

Create an HTTP session and connect via WebSocket for Inverse on mainnet:
```python
az = Perp(host="https://f-api.myaztests.com", access_key='', secret_key='')
```

Information can be sent to, or retrieved from, the AZ.COM APIs:
```python
print(az.get_account_capital())
```

## Examples
You can find more examples in the project folder /examples/

## Contact
You can reach out for support on the [AZAPI Telegram](https://localhost) group chat.
