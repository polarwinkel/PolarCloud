# PolarCloud
personal Cloud- and Wiki-like documentation server

## Alpha-State!

This is still in alpha-state, __not__ recommended for any production use yet!

## How to use

Run the app.py and point your Browser to localhost:5000

The files in `data` will be shown in your cloud.

There is just a tiny limitation for naming your files: Paths starting with `_` are reserved for internal use and the meta-information is stored in sidecar-files (yaml-format) ending with `.pcsc`.

## TODO:

- implement a quick-search on the index-page
- implement a server-based full-text-search
- handle different file formats differently, supporting editing a few text-based ones; Fallback: offer for download
- allow versioning of some file-formats using git
- separate file-index from meta-index for better performance
