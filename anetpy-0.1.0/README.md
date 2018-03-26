# Atlantic.Net Cloud API Python Wrapper

Inspired by [dop](https://github.com/ahmontero/dop).

## Installation

```bash
pip install anetpy
```

## Getting Started

To interact with Atlantic.Net Cloud, you first need .. an Atlantic.Net Cloud account with valid API keys.

Keys can be set either as Env variables, or within the code.

```bash
export ANET_PUBLIC_KEY='public_key'
export ANET_PRIVATE_KEY='private_key'
```

```python
>>> from anetpy.manager import AnetManager
>>> anet = AnetManager('public_key', 'private_key')
```

## Methods

The methods of the AnetManager are self explanatory; ex.

```python
>>> anet.all_active_cloudservers()
>>> anet.show_cloudserver('12345')
>>> anet.destroy_cloudserver('12345')
>>> anet.all_images()
>>> anet.all_ssh_keys()
>>> anet.plans()
>>> anet.new_cloudserver('new_cloudserver', 66, 1601, 1)
```