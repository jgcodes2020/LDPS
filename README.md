# LDPS
LDPS (Local Debian Package System) makes it easy to manage a local repository on Debian-based Linux distributions. It offers a command-line interface in the style of APT, making it easy to use, whoever you may be.

## Installation
This package is far from production-ready, and I don't think it belongs on PyPI just yet. If you are interested in testing it out, install as follows:

```sh
pip install .
```

The update scripts I've provided were made for personal use on the latest Ubuntu (at the time of last edit, 21.10 (impish)). However, they are likely to work for Ubuntu 20.04 (focal) and up.

## Notes
- Currently, the repository is hardcoded to /usr/local/debs.
- A malicious party has the ability to execute scripts as root, which is highly insecure.
