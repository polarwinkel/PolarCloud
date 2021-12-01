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
from datetime import datetime

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
    if os.path.isfile(folder+'/'+'index.mdtex'):
        with open(folder+'/'+'index.mdtex', 'r') as f:
            mdtex = f.read()
    else:
        mdtex = '(create an `index.mdtex` to show its content here)'
    content = mdtex2html.convert(mdtex)
    return render_template('index.html', relroot='./', filelist=filelist, content=content)

@app.route('/_static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

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
    meta = {}
    if os.path.isfile(folder+'/'+path+'.pcsc'):
        with open(folder+'/'+path+'.pcsc', 'r') as scF:
            meta = yaml.full_load(scF)
            if meta == None:
                meta = {}
    fileExt = os.path.splitext(folder+'/'+path)[1]
    if fileExt=='.mdtex' or fileExt=='.md':
        try:
            with open(folder+'/'+path, 'r') as f:
                mdtex = f.read()
        except FileNotFoundError:
            mdtex = '# 404 Error\n\nFile not found!'
        content = mdtex2html.convert(mdtex)
        return render_template('pageMdtex.html', relroot=relroot, path=path, content=content, meta=meta)
    elif fileExt == '.svg':
        try:
            with open(folder+'/'+path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            content = mdtex2html.convert('# 404 Error\n\nFile not found!')
        return render_template('pageSvg.html', relroot=relroot, path=path, content=content, meta=meta)
    else: 
        try:
            with open(folder+'/'+path, 'r') as f:
                mdtex = '['+path+']('+relroot+'_download/'+path+')'
        except FileNotFoundError:
            mdtex = '# 404 Error\n\nFile not found!'
        except IsADirectoryError:
            content = mdtex2html.convert('TODO: implement rename/delete')
            return render_template('pageDir.html', relroot=relroot, path=path, content=content)
        content = mdtex2html.convert(mdtex)
        return render_template('pageFile.html', relroot=relroot, path=path, content=content, meta=meta)

@app.route('/_download/<path:filename>', methods=['GET'])
def downloadFile(filename):
    '''download a file from the pagetree'''
    return send_from_directory(directory=folder, filename=filename)

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
@app.route('/_new/', defaults={'path': './'}, methods=['GET'])
def newPage(path):
    print(path)
    if path!='./':
        depth = path.count('/')
    else:
        depth=0
    relroot = '../'
    for i in range(depth):
        relroot = relroot+'../'
    return render_template('new.html', relroot=relroot, path=path)

@app.route('/_exists', methods=['GET'])
def exists():
    content = mdtex2html.convert('#ERROR: Name exists\n please go back and choose a different name.')
    return render_template('pageMdtex.html', relroot='./', path='./', content=content)

@app.route('/_createContent/<path:path>', methods=['POST'])
@app.route('/_createContent/', defaults={'path': './'}, methods=['POST'])
def createContent(path):
    #postvars = request.data.decode('utf-8') 
    #print(postvars)
    safechars = string.ascii_lowercase + string.ascii_uppercase + string.digits + '.-_'
    fname = ''.join([c for c in request.json['name'] if c in safechars])
    meta = False
    if request.json['type'] == 'mdtex':
        filename = fname+'.mdtex'
        meta = True
    elif request.json['type'] == 'svg':
        filename = fname+'.svg'
        meta = True
    elif request.json['type'] == 'folder':
        if os.path.isdir(folder+'/'+path+fname):
            return '_exists'
        else:
            os.mkdir(folder+'/'+path+fname)
            return '/'
    else:
        return 'ERROR 501: Type not implemented'
    filepath = folder+'/'+path+filename
    if os.path.isfile(filepath):
        return '_exists'
    else:
        with open(filepath, 'w') as f:
            f.write(str(request.json['source']))
        if meta:
            with open(filepath+'.pcsc', 'w') as f:
                m={}
                m['description'] = str(request.json['description'])
                m['keywords'] = str(request.json['keywords'])
                m['created'] = str(datetime.now())
                m['edited'] = str(datetime.now())
                yaml.dump(m, f, allow_unicode=True)
        return path+filename

@app.route('/_uploadFile/<path:path>', methods=['POST'])
@app.route('/_uploadFile/', defaults={'path': './'}, methods=['POST'])
def uploadFile(path):
    print(request.files)
    if 'file' not in request.files:
        return 'ERROR: no file received'
    uploadFile = request.files['file']
    # no file => empty file without filename:
    if uploadFile.filename == '':
        return 'ERROR: no filename received'
    if uploadFile:
        if request.form.get('name') == '':
            filename = uploadFile.filename;
        else:
            filename = request.form.get('name')+os.path.splitext(uploadFile.filename)[1]
        filepath = folder+'/'+path
        if os.path.isfile(filepath):
            return '_exists'
        uploadFile.save(os.path.join(filepath, filename))
        with open(filepath+filename+'.pcsc', 'w') as f:
            m={}
            m['description'] = str(request.form.get('description'))
            m['keywords'] = str(request.form.get('keywords'))
            m['created'] = str(datetime.now())
            m['edited'] = str(datetime.now())
            yaml.dump(m, f, allow_unicode=True)
    return path+'/'+filename

@app.route('/_mdtex2html', methods=['POST'])
def post_mdtex2html():
    postvars = request.data
    try:
        return mdtex2html.convert(postvars.decode("utf-8"), extensions)
    except Exception as e:
        return 'ERROR: Could not convert the mdTeX to HTML:' + str(e)

@app.route('/_updatePage/<path:path>', methods=['PUT'])
def updatePage(path):
    postvars = request.data.decode('utf-8') 
    filepath = folder+'/'+path
    with open(filepath, 'w') as f:
        f.write(str(postvars))
    if os.path.isfile(folder+'/'+path+'.pcsc'):
        with open(filepath+'.pcsc', 'r') as mf:
            try:
                m = yaml.safe_load(mf)
            except:
                m = {}
    else:
        m = {}
    with open(filepath+'.pcsc', 'w') as mf:
        m['edited'] = str(datetime.now())
        yaml.dump(m, mf, allow_unicode=True)
    return '0'

@app.route('/_updateMeta/<path:path>', methods=['PUT'])
def updateMeta(path):
    postvars = request.data.decode('utf-8')
    filepath = folder+'/'+path+'.pcsc'
    #print(yaml.dump(postvars, allow_unicode=True))
    if os.path.isfile(folder+'/'+path+'.pcsc'):
        with open(filepath, 'r') as f:
            try:
                m = yaml.safe_load(f)
            except:
                m = {}
    else:
        m = {}
    with open(filepath, 'w') as f:
        m['edited'] = str(datetime.now())
        mNeu = json.loads(postvars)
        m['description'] = mNeu['description']
        m['keywords'] = mNeu['keywords']
        yaml.dump(m, f, allow_unicode=True)
    return '0'

@app.route('/_move/<path:path>', methods=['PUT'])
def move(path):
    print(request.data.decode('utf-8'))
    data = json.loads(request.data.decode('utf-8'))
    if 'filename' in data:
        filename = data['filename']
    else:
        filename = os.path.basename(path)
    if os.path.isfile(folder+'/'+data['destPath']+'/'+filename):
        return 'ERROR: file exists'
    os.rename(folder+'/'+path, folder+'/'+data['destPath']+'/'+filename)
    fileMetaPath = folder+'/'+path+'.pcsc'
    if os.path.exists(fileMetaPath):
        os.rename(fileMetaPath, folder+'/'+data['destPath']+'/'+filename+'.pcsc')
    return '0'

@app.route('/_updateSettings', methods=['PUT'])
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

@app.route('/_delete/<path:path>', methods=['DELETE'])
def deletePage(path):
    if os.path.exists(folder+'/'+path):
        os.remove(folder+'/'+path)
        if os.path.exists(folder+'/'+path+'.pcsc'):
            os.remove(folder+'/'+path+'.pcsc')
        return '0'
    else:
        return 'ERROR: file not found!'

@app.errorhandler(404)
def error_not_found(error):
    return render_template('404.html'), 404

# run it:

if __name__ == '__main__':
    app.run(host=host, debug=debug)
