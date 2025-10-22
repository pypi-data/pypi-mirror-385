# sequenceutils

[![PyPI - Version](https://img.shields.io/pypi/v/sequenceutils.svg)](https://pypi.org/project/sequenceutils)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sequenceutils.svg)](https://pypi.org/project/sequenceutils)

-----

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

```console
pip install sequenceutils
```

## Usage

### ComputedSequence

`ComputedSequence` can be used to create a sequence from a function and a given length. Upon indexing, the function is called to compute the value at the given index.

```python
from sequenceutils import ComputedSequence

# Create a sequence from a function and a given length
seq = ComputedSequence(lambda i: i + 1, length=10)

# Access elements from the sequence
print(seq[0])  # 1
print(seq[5])  # 6
print(seq[-1])  # 10

# Slicing is fully supported
print(list(seq[1:4]))  # [2, 3, 4]
print(list(seq[::2]))  # [1, 3, 5, 7, 9]
```

After turning a function (over the non-negative integers) into a `ComputedSequence`, you can use any method that operates on a `Sequence`. For example, this makes it easy to implement the inverse of a monotonically increasing function using `bisect`:

```python
from sequenceutils import ComputedSequence
import bisect

def floor_root(y):
    """Computes the floor of the square root of y (up to 10^9)"""
    seq = ComputedSequence(lambda x: x * x, length=10**9)
    return bisect.bisect_right(seq, y) - 1

print(floor_root(4))  # 2
print(floor_root(5))  # 2
print(floor_root(16))  # 4
```

Item assignment is not supported.

### ConcatenatedSequence

With `ConcatenatedSequence`, you can create a single sequence from multiple sequences. Rather than creating a new, larger container in memory, `ConcatenatedSequence` determines which sequence to index based on the index of the requested element. Thus, this class is suitable for creating (very) large sequences in situations where doing so in memory is impractical.

```python
from sequenceutils import ConcatenatedSequence

# Create a sequence from multiple sequences
seq = ConcatenatedSequence([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# Access elements from the concatenated sequence
print(seq[0])  # 1
print(seq[5])  # 6
print(seq[-1])  # 9

# Slicing is fully supported
print(seq[1:4])  # [2, 3, 4]
print(seq[::2])  # [1, 3, 5, 7, 9]
```

In conjunction with `ComputedSequence`, this can be used to create the concatenation of lazily computed sequences:

```python
from sequenceutils import ConcatenatedSequence, ComputedSequence

seq = ConcatenatedSequence([
    ComputedSequence(lambda i: i + 1, length=5),
    ComputedSequence(lambda i: i + 10, length=5)
])

print(list(seq))  # [1, 2, 3, 4, 5, 10, 11, 12, 13, 14]
```

Like with `ComputedSequence`, item assignment is not supported.

## License

`sequenceutils` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
