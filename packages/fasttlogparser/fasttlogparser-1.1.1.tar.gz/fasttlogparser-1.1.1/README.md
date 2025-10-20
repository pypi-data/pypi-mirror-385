# ⚡ fasttlogparser - Blazing-Fast MAVLink .tlog Parser

[![codecov](https://codecov.io/gh/Bogdanov-am/fasttlogparser/graph/badge.svg?token=UNPLPI04DR)](https://codecov.io/gh/Bogdanov-am/fasttlogparser)
![test](https://github.com/Bogdanov-am/fasttlogparser/actions/workflows/python-test.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/fasttlogparser.svg)](https://badge.fury.io/py/fasttlogparser)

**Unlock lightning-fast MAVLink telemetry parsing** with this Python package powered by optimized C++ backend. Extract insights from .tlog files at unparalleled speeds!

```python
import fasttlogparser

# Parse entire file
messages, msg_ids = fasttlogparser.parseTLog("flight.tlog")

# Advanced: Filter messages + remap fields
results = fasttlogparser.parseTLog(
    path = "mission.tlog",
    ids = [(1,1)],                              # Specific MAVLink IDs
    whitelist = ["GPS_RAW_INT", "ATTITUDE"],    # Keep only these messages
    blacklist = ["AUTOPILOT_VERSION"],          # Exclude these messages
    remap_field = {"alt": "altitude"}           # Rename fields
)
```

## ✨ Key Features

- **Native C++ acceleration** - ~100x faster than pure Python parser
- **Smart filtering** - by system_id/componet_id or message name whitelist/blacklist
- **Field remapping** - customize output schema
- **Zero dependencies** - lightweight Python bindings via pybind11

## ⚙️ Installation

```bash
pip install fasttlogparser --no-build-isolation
```

## 🔧 Advanced Usage

Filter messages using MAVLink IDs:

```python
# Get only GPS_RAW_INT and ATTITUDE messages
messages = fasttlogparser.parseTLog("data.tlog", whitelist=["GPS_RAW_INT", "ATTITUDE"])
```

Filter messages using system and component IDs:

```python
# Keep only (2,1) - (sysId, cmpId)
results = fasttlogparser.parseTLog("long_flight.tlog", ids = [(2,1)])
```

Rename individual message fields:

```python
results = fasttlogparser.parseTLog("long_flight.tlog", remap_field = {"alt": "altitude"})
```

## ⚡ Benchmark

Processing a 252MB .tlog file:

- Pure Python parser: 24m 56s ⏳
- **fasttlogparser**: 16.6s ⚡ _(90x faster!)_

---

### Ready for high-performance telemetry MAVLink analysis?
