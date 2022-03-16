# LDPS
LDPS (Local Debian Package System) makes it easy to manage a local repository on Debian-based Linux distributions. It offers a command-line interface in the style of APT, making it easy to use, whoever you may be.

## Notes
- Currently, the repository is hardcoded to /usr/local/debs.
- Installation must be done manually.
  - Copy `ldps` to `/usr/local/bin/ldps`.
  - Update scripts go to `/etc/ldps/autoupdate.d`
- A malicious party has the ability to execute scripts as root, which is highly insecure.
