# dictop

DICT-OPERATION allow you select data value from a dict-instance with dot separated path, and update.

## Install

```
pip install dictop
```

## Test Passed On Python

- 2.7
- 3.2
- 3.3
- 3.4
- 3.5
- 3.6
- 3.7
- 3.8
- 3.9
- 3.10
- 3.11

## Usage

```
    from dictop import update
    from dictop import select

    data = {}
    update(data, "a.b.c", 2)
    assert select(data, "a.b.c") == 2
```

## Core Functions

1. select

```
    select(target, path, default=None, slient=True)
```

2. update

```
    update(target, path, value)
```
## Unit Tests

```
# tests.py

import unittest
import dictop

class DictopTest(unittest.TestCase):


    def test01(self):
        data = {
            "a": {
                "b": "value",
            }
        }
        assert dictop.select(data, "a.b") == "value"
        assert dictop.select(data, "a.c") is None
    
    def test02(self):
        data = {
            "a": [{
                "b": "value",
            }]
        }
        assert dictop.select(data, "a.0.b") == "value"
        assert dictop.select(data, "a.1.b") is None

    def test03(self):
        data = [1,2,3]
        assert dictop.select(data, "0") == 1
        assert dictop.select(data, "4") is None

    def test04(self):
        data = {}
        dictop.update(data, "a.b.c", "value")
        dictop.select(data, "a.b.c") == "value"
    
    def test05(self):
        data = []
        dictop.update(data, "1.a.b", "value")
        assert data[1]["a"]["b"] == "value"
```

## Releases

### 0.1.0 2018/03/20

- First release.

### 0.1.1 2018/03/20
### 0.1.2 2018/04/02
### 0.1.3 2018/04/18
### 0.1.4 2019/04/12

- Update.

### 0.2.1 2022/01/08

- Fix license file missing problem.

### 0.2.2 2023/09/08

- Add gitlab-ci and tested on all python versions.

### 0.2.3 2025/10/21

- Doc update.
