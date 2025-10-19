# haut_scanner

An asynchronous toolkit for discovering HAUT services. The initial module targets HAUT JWGLXT portals and records reachable instances for later analysis.

## Installation

```bash
pip install haut_scanner
```

## Usage

Run the bundled command-line interface:

```bash
haut_scan
```

Or integrate the scanner into your own script:

```python
from haut_scanner import JwglxtScanner
import asyncio

async def main():
    scanner = JwglxtScanner()
    await scanner.scan()
    scanner.save_results("jwglxt_urls.json")

asyncio.run(main())
```

The scan writes any discovered portals to `jwglxt_urls.json` by default.

## Development

This project uses Hatch for builds. To produce a wheel and source distribution:

```bash
hatch build
```
