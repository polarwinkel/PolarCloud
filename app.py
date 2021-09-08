#!/usr/bin/python3
#coding: utf-8
'''
Flask wsgi-interface for PolarCloud
'''

import os, sys
from flask import Flask, render_template, request, send_from_directory, make_response, jsonify
import json, yaml, string
from jinja2 import Template
import mdtex2html
from modules import settingsio, load

folder='data' # TODO: include in settings!

# global settings:

setfile = 'settings.yaml'

app = Flask(__name__)
settings = settingsio.settingsIo(setfile)

host = settings.get('host')
debug = settings.get('debug')
# extensions to be used by python-markdown:
extensions = settings.get('extensions')

# routes:

@app.route('/', methods=['GET'])
def index():
    '''show index-page'''
    files = load.loadFolder(folder)
    #print(json.dumps(files, indent=4, sort_keys=True)) # show files-dict for debugging and reference
    filelist = json.dumps(files)
    return render_template('index.html', relroot='./', filelist=filelist)

#@app.route('/data', methods=['GET'])
#def sendData():
#    return render_template('data.html', relroot='./')

@app.route('/<path:path>', methods=['GET'])
def page(path):
    '''show wiki-page'''
    depth = path.count('/')
    relroot = './'
    for i in range(depth):
        relroot = relroot+'../'
    # TODO: different handling depending on file ending, download for unknown
    try:
        with open(folder+'/'+path, 'r') as f:
            mdtex = f.read()
    except FileNotFoundError:
        mdtex = '# 404 Error\n\nFile not found!'
    except IsADirectoryError:
        mdtex = '# 501 Error\n\nDirectory listing is not implemented!'
    content = mdtex2html.convert(mdtex)
    meta = {}
    if os.path.isfile(folder+'/'+path+'.pcsc'):
        with open(folder+'/'+path+'.pcsc', 'r') as scF:
            meta = yaml.full_load(scF)
    return render_template('page.html', relroot=relroot, path=path, content=content, meta=meta)

@app.route('/_mdTeXCheatsheet', methods=['GET'])
def sendMdTeXCheatSheet():
    return render_template('mdTeXCheatsheet.html', relroot='./')

@app.route('/_settings', methods=['GET'])
def sendSettings():
    return render_template('settings.html', relroot='./', settings=settings.getJson())

@app.route('/_getSource/<path:path>', methods=['GET'])
def getSource(path):
    with open(folder+'/'+path, 'r') as f:
        page = f.read()
    return page

@app.route('/_new/<path:path>', methods=['GET'])
def newPage(path):
    depth = path.count('/')
    relroot = '../'
    for i in range(depth):
        relroot = relroot+'../'    
    return render_template('new.html', relroot=relroot, path=path)

@app.route('/createContent/<path:path>', methods=['POST'])
def createContent(path):
    #postvars = request.data.decode('utf-8') 
    #print(postvars)
    safechars = string.ascii_lowercase + string.ascii_uppercase + string.digits + '.-_'
    fname = ''.join([c for c in request.json['name'] if c in safechars])
    if request.json['type'] == 'mdtex':
        filename = fname+'.mdtex'
    elif request.json['type'] == 'svg':
        filename = fname+'.svg'
    elif request.json['type'] == 'folder':
        os.mkdir(folder+'/'+path+'/'+fname)
        return '/'
    else:
        return 'TODO: Error'
    filepath = folder+'/'+path+'/'+filename
    with open(filepath, 'w') as f:
        f.write(str(request.json['source']))
    return path+'/'+filename

@app.route('/mdtex2html', methods=['POST'])
def post_mdtex2html():
    postvars = request.data
    try:
        return mdtex2html.convert(postvars.decode("utf-8"), extensions)
    except Exception as e:
        return 'ERROR: Could not convert the mdTeX to HTML:' + str(e)

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
