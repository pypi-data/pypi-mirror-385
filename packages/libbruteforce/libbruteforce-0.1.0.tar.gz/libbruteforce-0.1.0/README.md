<!--suppress HtmlDeprecatedAttribute-->
<div align="center">
   <h1>💥 python-libbruteforce</h1>

[![Coverage](https://img.shields.io/badge/coverage-0%25-red)](https://github.com/Jayson-Fong/python-libbruteforce)
[![Latest Version](https://img.shields.io/pypi/v/libbruteforce.svg)](https://pypi.org/project/libbruteforce/)
[![Python Versions](https://img.shields.io/pypi/pyversions/libbruteforce.svg)](https://pypi.org/project/libbruteforce/)
[![Format](https://img.shields.io/pypi/format/libbruteforce.svg)](https://pypi.org/project/libbruteforce/)
[![License](https://img.shields.io/pypi/l/libbruteforce)](https://github.com/Jayson-Fong/libbruteforce/)
[![Status](https://img.shields.io/pypi/status/libbruteforce)](https://pypi.org/project/libbruteforce/)
[![Types](https://img.shields.io/pypi/types/libbruteforce)](https://pypi.org/project/libbruteforce/)


</div>

<hr />

<div align="center">

[💼 Purpose](#purpose) | [🛠️ Installation](#installation) | [⚙️ Usage](#usage) | [⚖️ Notice](#notice)

</div>

<hr />

# Purpose

This package provides Python bindings for the [libbruteforce](https://crates.io/crates/libbruteforce) Rust crate in
an effort to offer increased flexibility in scripting for red-teaming exercises and capture-the-flag competitions, 
particularly when the goal is to identify potentially compromised credentials or weak credentials.

This package primarily leverages a defined alphabet alongside a minimum and maximum message length unlike traditional
password cracking tools, which typically use wordlists. Due to the sheer number of possible combinations, brute-forcing
a password is often a very time-consuming process, and using this library is likely infeasible unless you have a
constrained enough alphabet or the message length is considerably short.

With its Rust-based backend and the usage of true multi-threading, this package can brute-force passwords consisting of
four ASCII printable characters nearly instantly on a modern machine. As can be expected, messages of longer lengths,
and especially those with a large alphabet, will take longer to brute-force.

# Installation

You can install BullCrypt from [PyPI](https://pypi.org/project/libbruteforce/):

```shell
python -m pip install libbruteforce
```

For the latest development builds, you can install from GitHub:

```shell
python -m pip install git+https://github.com/Jayson-Fong/python-libbruteforce
```

# Usage

To start cracking, you need to decide on an alphabet. You may either provide a Python `str` object or use the provided
`AlphabetBuilder` class to generate an alphabet. When using `AlphabetBuilder`, characters are automatically deduplicated
and certain methods are provided for convenience to add common character sets.

For example, to create an alphabet consisting of lowercase letters and the character "!":

```python
from libbruteforce import AlphabetBuilder


alphabet: AlphabetBuilder = AlphabetBuilder().with_lowercase().with_char("!")
```

You must then create a cracking parameters object, which consists of the alphabet, the algorithm to use, the minimum
and maximum message length, and whether to operate greedily on resources. In this example, we choose to use our
previously defined alphabet, the MD5 algorithm, a minimum message length of 0, a maximum message length of 5, and
to operate greedily on resources.

```python
from libbruteforce import AlphabetBuilder, BasicCrackParameter, Algorithm


alphabet: AlphabetBuilder = AlphabetBuilder().with_lowercase().with_char("!")
params: BasicCrackParameter = BasicCrackParameter(alphabet, Algorithm.MD5, 0, 4, True)
```

Currently, the MD5, SHA1, and SHA256 algorithms are supported. You may also specify the _identity_ algorithm, which does
not perform any hashing; however, it can be used to evaluate at which point a message is attempted and to test whether
the program is operating correctly.

Algorithms are identified by an integer, but it is recommended to use the `Algorithm` class attributes to access them
in case they are updated in the future.

To convert the alphabet into a `str`, you can use the `AlphabetBuilder.build()` method; however, usage of the alphabet
for cracking does not mandate this and either an `AlphabetBuilder` instance or `str` object may be passed to create
a `BasicCrackParameter` instance.

Once the `BasicCrackParameter` is constructed, it can be passed to the `crack` function alongside the hash to crack.
The content of the hash is run through a basic sanity check to ensure that it is a valid hash for the chosen algorithm
and may produce an exception if it is not. Upon successfully cracking the message, a string of the message is returned.
If the cracking job completes without finding a match, `None` is returned.

```python
import libbruteforce

alphabet = libbruteforce.AlphabetBuilder().with_lowercase().with_digits()
params = libbruteforce.BasicCrackParameter(alphabet, libbruteforce.Algorithm.MD5, 0, 5, True)
print(libbruteforce.crack(params, "b2f3d1e0efcb5d60e259a34ecbbdbe00"))
```

# Backlog

For future implementation:

- [ ] Command-line utility
- [ ] Automatic hash type detection
- [ ] Python type stubs

# Notice

While this software is provided under the MIT License, the author does **not** endorse or condone any unlawful,
unethical, or harmful use of this software.
