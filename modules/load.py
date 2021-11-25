#!/usr/bin/python3
'''
load files for PolarCloud
'''

import os, glob, yaml

def getFromDict(dic, keys):    
    for key in keys:
        dic = dic[key]
    return dic

def setInDict(dic, keys, name, filename, ext, scYaml=''):
    if keys != ['']:
        for key in keys:
            dic = dic.setdefault(key, {})
    if not '.' in dic.keys():
        dic['.'] = {}
    if filename != '':
        dic['.'][filename] = {'name': name, 'ext': ext, 'scYaml':scYaml}
    elif name != '':
        if not name in dic:
            dic[name] = {}

def loadFolder(folder):
    '''recursive search for files in a folder, returning as dict, with sc.yaml as additional "sidecar-info"'''
    pages={}
    files = sorted(glob.glob(folder+'/**', recursive=True))
    for f in files:
        if not f.endswith('.pcsc') and os.path.isfile(f):
            filename=os.path.basename(f)
            name=os.path.splitext(filename)[0]
            ext=os.path.splitext(filename)[1]
            path = os.path.dirname(f)[len(folder)+1:]
            pl = path.split('/')
            #scFile = os.path.splitext(f)[0]+'.pcsc'
            scFile = os.path.relpath(f)+'.pcsc'
            meta = {}
            if os.path.isfile(scFile):# TODO: Keywords and description separate!
                with open(scFile, 'r') as scF:
                    meta = yaml.full_load(scF)
            setInDict(pages, pl, name, filename, ext, meta)
        elif not os.path.isfile(f):
            filename=os.path.basename(f)
            name=os.path.splitext(filename)[0]
            ext=os.path.splitext(filename)[1]
            path = os.path.dirname(f)[len(folder)+1:]
            pl = path.split('/')
            setInDict(pages, pl, name, '', '')
    return pages
