# Interfaced

Python interface system

## Install

```bash
pip install interfaced
```

## Quick Start

```python
from interfaced import interface, implements, is_implementation

@interface
class DataStore:
    def save(self, data: str) -> bool: ...
    async def load(self, id: str) -> str: ...

@implements(DataStore)
class MemoryStore:
    def save(self, data: str) -> bool:
        return True
    
    async def load(self, id: str) -> str:
        return "data"

store = MemoryStore()
print(is_implementation(store, DataStore))  # True
```

## Features

- Strict type enforcement for methods and attributes
- Generic interfaces with type variables  
- Zero configuration required
