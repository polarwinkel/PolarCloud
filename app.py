#!/usr/bin/python3
#coding: utf-8
'''
Flask wsgi-interface for PolarCloud
'''

import os, sys
from flask import Flask, render_template, request, send_from_directory, make_response, jsonify
import json, yaml
from jinja2 import Template
from base64 import b64encode, b64decode, decodebytes
from io import BytesIO
from PIL import Image
import mdtex2html
from modules import settingsio, load

folder='pages' # TODO: include in settings!

# global settings:

setfile = 'settings.yaml'

app = Flask(__name__)
settings = settingsio.settingsIo(setfile)

pages = load.loadFolder(folder)
print(json.dumps(pages, indent = 4))
host = settings.get('host')
debug = settings.get('debug')
# extensions to be used by python-markdown:
extensions = settings.get('extensions')

# routes:

@app.route('/', methods=['GET'])
def index():
    '''show index-page'''
    pagelist = json.dumps(pages)
    return render_template('index.html', relroot='./', pagelist=pagelist)

@app.route('/data', methods=['GET'])
def sendData():
    return render_template('data.html', relroot='./')

@app.route('/pages/<path:path>', methods=['GET'])
def page(path):
    '''show wiki-page'''
    depth = path.count('/')
    relroot = '../'
    for i in range(depth):
        relroot = relroot+'../'
    try:
        with open(folder+'/'+path, 'r') as f:
            page = f.read()
    except FileNotFoundError:
        page = '# 404 Error\n\nFile not found!'
    except IsADirectoryError:
        page = '# 501 Error\n\nDirectory listing is not implemented!'
    content = mdtex2html.convert(page)
    return render_template('page.html', relroot=relroot, path=path, content=content)

@app.route('/mdTeXCheatsheet', methods=['GET'])
def sendMdTeXCheatSheet():
    return render_template('mdTeXCheatsheet.html', relroot='./')

@app.route('/settings', methods=['GET'])
def sendSettings():
    return render_template('settings.html', relroot='./', settings=settings.getJson())

@app.route('/getSource/<path:path>', methods=['GET'])
def getSource(path):
    with open(folder+'/'+path, 'r') as f:
        page = f.read()
    return page

@app.route('/mdtex2html', methods=['POST'])
def post_mdtex2html():
    postvars = request.data
    try:
        return mdtex2html.convert(postvars.decode("utf-8"), extensions)
    except Exception as e:
        return 'ERROR: Could not convert the mdTeX to HTML:' + str(e)

@app.route('/new', methods=['GET'])
def newPage():
    return 'TODO'

@app.route('/updatePage/<path:path>', methods=['PUT'])
def updatePage(path):
    postvars = request.data.decode('utf-8') 
    filepath = folder+'/'+path
    with open(filepath, 'w') as f:
        f.write(str(postvars))
    return '0'

@app.route('/updateSettings', methods=['PUT'])
def updateSettings():
    setnew = request.json
    if 'False' in setnew['extensions']:
        setnew['extensions'] = list(dict.fromkeys(setnew['extensions']))
        setnew['extensions'].remove('False')
    settings.set(setnew, setfile)
    global host
    host = settings.get('host')
    global debug
    debug = settings.get('debug')
    global extensions
    extensions = settings.get('extensions')
    content = 'ok'
    return content

@app.route('/delete', methods=['DELETE'])
# TODO
def deletePage():
    result = 'TODO'
    return result

@app.errorhandler(404)
def error_not_found(error):
    return render_template('404.html'), 404

# run it:

if __name__ == '__main__':
    app.run(host=host, debug=debug)
