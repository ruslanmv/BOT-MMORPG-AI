# Interception driver — third-party redistribution

This directory bundles the Interception driver toolkit by Francisco Lopes
(github user @oblitum) so that BOT-MMORPG-AI can install the kernel-mode
driver during application setup.

## Upstream source

- Project: https://github.com/oblitum/Interception
- Release used: **v1.0.1**
- Release page: https://github.com/oblitum/Interception/releases/tag/v1.0.1
- Release archive (authoritative): https://github.com/oblitum/Interception/releases/download/v1.0.1/Interception.zip

Anything outside the official GitHub repository / Releases page is **not
trusted** — re-uploaded zips and "patched" forks are a known malware
vector for this driver. Only re-bundle from the upstream archive above.

## What is shipped here

```
src-tauri/drivers/interception/
├── install-interception.exe                    Driver installer (LFS-tracked)
├── library/
│   ├── interception.h                          C API header
│   ├── x64/
│   │   ├── interception.dll                    64-bit runtime DLL
│   │   └── interception.lib                    64-bit import library
│   └── x86/
│       ├── interception.dll                    32-bit runtime DLL
│       └── interception.lib                    32-bit import library
├── licenses/
│   ├── commercial-usage/
│   │   ├── Interception-API.pdf                Commercial API license
│   │   └── Interception.pdf                    Commercial driver license
│   └── non-commercial-usage/
│       └── LGPL-3.0.txt                        LGPL 3.0 (default OSS terms)
└── NOTICE.md                                   This file
```

## Integrity verification

`install-interception.exe` is identical to the file inside the official
release archive's `command line installer/` folder.

| Property | Value |
|---|---|
| Size | 470,528 bytes |
| SHA-256 | `e137863a79da797f08e7a137280ff2a123809044a888fd75ce9c973198915abe` |

The repository tracks this file via Git LFS (see `.gitattributes`); a
fresh clone needs `git lfs pull` to materialize the real binary. Without
LFS the working copy contains only the 131-byte LFS pointer, which is
why the build pipeline asserts a real-size check before bundling.

## License

Interception is dual-licensed:

- **Non-commercial use** is covered by the LGPL 3.0
  (`licenses/non-commercial-usage/LGPL-3.0.txt`).
- **Commercial use** requires a separate paid license from the upstream
  author (see PDFs in `licenses/commercial-usage/`).

If BOT-MMORPG-AI is being used or distributed commercially, the
deployer is responsible for obtaining a commercial Interception license
from oblitum. Bundling these files in the installer is permitted by the
upstream license terms (we redistribute unmodified, and we ship the
licenses alongside the binary).

## Filename note

The two upstream filenames `Interception API.pdf` and `LGPL 3.0.txt`
have spaces, which (a) NSIS' `File /oname=` directive cannot handle
cleanly without quoting, and (b) our build pipeline preflight rejects
to keep makensis happy. Renamed in this tree to:

- `Interception API.pdf` → `Interception-API.pdf`
- `LGPL 3.0.txt`         → `LGPL-3.0.txt`

Contents are byte-identical to upstream — only the filename differs.

## Sample programs

The official zip also contains `samples/x86/*.exe` (axes, cadstop,
caps2esc, hardwareid, identify, mathpointer, x2y) demonstrating use of
the API. Those are NOT bundled here — they're not needed at runtime,
they're 32-bit, and adding them via Git LFS requires a build-host with
`git-lfs` installed. Pull them from the official release zip if needed
for development.
