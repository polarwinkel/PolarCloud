# PolarCloud
personal Cloud- and Wiki-like documentation server

## What is this

PolarCloud is lightweight replacement for a personal wiki or a personal cloud storage.

I have been using different personal cloud- and wiki-solutions like OwnCloud/NextCloud, TiddlyWiki, DokuWiki and Gollum Wiki. All of them had their individual benefits, but no Wiki ever made it to be a real "daily driver".

Large million-lines-of-code Cloud soutions were too fat to maintain, lightweight wiki-solutions were lacking file-hosting and an organization structure: I kept forgetting that I had information already. That's why I decided to create my own tool.

PolarCloud is a file-based personal documentation-platform using markdown-format, enriched with the possibility to include mathematical formulas in LaTeX-format (see my [mdTeX2html-library](https://github.com/polarwinkel/mdtex2html)).

The client-side, lightning-fast search for keywords makes it very snappy to use. The tree-structure takes care that you keep the overview of your documentations. And when you need a different file-type like an image or whatever you have just upload it.

On the backend-side you just have your file-structure, can edit all the files as well on your host and therefore use your favourite sync-tool line unison or rsync to syncronize or backup your data.

## How to use

The quick-way: Run the app.py and point your Browser to localhost:5000

The production-way: Use a WSGI-Server like Gunicorn: `nohup gunicorn3 app:app -n pc -w 2 -b 192.168.x.y:4204` will make it accessible in your Network on the given port. A Raspi is fine for that. 

The secure-way: Use a reverse-proxy like nginx, Apache, LightHttpd, ... to add authentification, i.e. with BasicAuth.

The files in `data` will be shown in your cloud.

## Limitations

There is a tiny limitation for naming your files: Paths starting with `_` are reserved for internal use, and the meta-information is stored in sidecar-files (yaml-format) ending with `.pcsc`.

Keep in mind that PolarCloud has no security implementations at all - use a proxy or a vpn or similar to add access-control! Then you just need to care about security-updates for that and never care about patching PolarCloud!

## TODO:

Theese features might come some time, but no promises are given! Feel free to contact me if you like one of theese or have a different good idea!

- implement a server-based full-text-search
- allow versioning of some file-formats using git
