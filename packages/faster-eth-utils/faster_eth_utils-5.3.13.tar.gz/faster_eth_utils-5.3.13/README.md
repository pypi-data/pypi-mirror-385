### I forked eth-utils and compiled it to C. It does the same stuff, now faster

[![PyPI](https://img.shields.io/pypi/v/faster-eth-utils.svg?logo=Python&logoColor=white)](https://pypi.org/project/faster-eth-utils)
[![Monthly Downloads](https://img.shields.io/pypi/dm/faster-eth-utils)](https://pypistats.org/packages/faster-eth-utils)
[![Codspeed.io Status](https://img.shields.io/endpoint?url=https://codspeed.io/badge.json)](https://codspeed.io/BobTheBuidler/faster-eth-utils)

##### This fork will be kept up-to-date with [eth-utils](https://github.com/ethereum/eth-utils). I will pull updates as they are released and push new [faster-eth-utils](https://github.com/BobTheBuidler/faster-eth-utils) releases to [PyPI](https://pypi.org/project/faster-eth-utils/).

##### Starting in [v5.3.11](https://github.com/BobTheBuidler/faster-eth-utils/releases/tag/v5.3.11), all `faster-eth-utils` Exception classes inherit from the matching Exception class in `eth-utils`, so porting to `faster-eth-utils` does not require any change to your existing exception handlers. All existing exception handling in your codebase will continue to work as it did when originaly implemented.

##### We benchmark `faster-eth-utils` against the original `eth-utils` for your convenience. [See results](https://github.com/BobTheBuidler/faster-eth-utils/tree/master/benchmarks/results).

##### You can find the compiled C code and header files in the [build](https://github.com/BobTheBuidler/eth-utils/tree/master/build) directory.

###### You may also be interested in: [faster-web3.py](https://github.com/BobTheBuidler/faster-web3.py/), [faster-eth-abi](https://github.com/BobTheBuidler/faster-eth-abi/), and [faster-hexbytes](https://github.com/BobTheBuidler/faster-hexbytes/)

##### The original eth-utils readme is below:

# Ethereum Utilities

[![Join the conversation on Discord](https://img.shields.io/discord/809793915578089484?color=blue&label=chat&logo=discord&logoColor=white)](https://discord.gg/GHryRvPB84)
[![Build Status](https://circleci.com/gh/ethereum/eth-utils.svg?style=shield)](https://circleci.com/gh/ethereum/eth-utils)
[![PyPI version](https://badge.fury.io/py/eth-utils.svg)](https://badge.fury.io/py/eth-utils)
[![Python versions](https://img.shields.io/pypi/pyversions/eth-utils.svg)](https://pypi.python.org/pypi/eth-utils)
[![Docs build](https://readthedocs.org/projects/eth-utils/badge/?version=latest)](https://eth-utils.readthedocs.io/en/latest/?badge=latest)

Common utility functions for python code that interacts with Ethereum

Read the [documentation](https://eth-utils.readthedocs.io/).

View the [change log](https://eth-utils.readthedocs.io/en/latest/release_notes.html).

## Installation

```sh
python -m pip install eth-utils
```

## Developer Setup

If you would like to hack on eth-utils, please check out the [Snake Charmers
Tactical Manual](https://github.com/ethereum/snake-charmers-tactical-manual)
for information on how we do:

- Testing
- Pull Requests
- Documentation

We use [pre-commit](https://pre-commit.com/) to maintain consistent code style. Once
installed, it will run automatically with every commit. You can also run it manually
with `make lint`. If you need to make a commit that skips the `pre-commit` checks, you
can do so with `git commit --no-verify`.

### Development Environment Setup

You can set up your dev environment with:

```sh
git clone git@github.com:ethereum/eth-utils.git
cd eth-utils
virtualenv -p python3 venv
. venv/bin/activate
python -m pip install -e ".[dev]"
pre-commit install
```

### Update Networks

The list of networks resides in the JSON file under eth_utils/\_\_json/eth_networks.json.
This file is used to initialize Networks, which can be used to obtain network
information with a chain ID.

Run the script to update the JSON file with the response from the remote list.

```sh
python update_networks.py
```

If there are new networks they will appear in the JSON file. After checking the updates,
open a PR to make them available in a new release.

### Release setup

To release a new version:

```sh
make release bump=$$VERSION_PART_TO_BUMP$$
```

#### How to bumpversion

The version format for this repo is `{major}.{minor}.{patch}` for stable, and
`{major}.{minor}.{patch}-{stage}.{devnum}` for unstable (`stage` can be alpha or beta).

To issue the next version in line, specify which part to bump,
like `make release bump=minor` or `make release bump=devnum`. This is typically done from the
main branch, except when releasing a beta (in which case the beta is released from main,
and the previous stable branch is released from said branch).

If you are in a beta version, `make release bump=stage` will switch to a stable.

To issue an unstable version when the current version is stable, specify the
new version explicitly, like `make release bump="--new-version 4.0.0-alpha.1 devnum"`
