#!/usr/bin/python3
'''
Database-IO-file of TeXerBase - an Database Server for Exercises
'''

import os, glob

def getFromDict(dic, keys):    
    for key in keys:
        dic = dic[key]
    return dic

def setInDict(dic, keys, name, filename, ext, scYaml):
    if keys != ['']:
        for key in keys:
            dic = dic.setdefault(key, {})
    if not '.' in dic.keys():
        dic['.'] = {}
    dic['.'][filename] = {'name': name, 'ext': ext, 'scYaml':scYaml}
    
def loadFolder(folder):
    '''loads all .md, .mdt and .mdtex-files from a folder, returning as dict'''
    pages={}
    files = glob.glob(folder+'/**', recursive=True)
    for f in files:
        if not f.endswith('.sc.yaml') and os.path.isfile(f):
            filename=os.path.basename(f)
            name=os.path.splitext(filename)[0]
            ext=os.path.splitext(filename)[1]
            path = os.path.dirname(f)[len(folder)+1:]
            pl = path.split('/')
            scFile = os.path.splitext(f)[0]+'.sc.yaml'
            scYaml = ''
            if os.path.isfile(scFile):
                with open(scFile, 'r') as scF:
                    scYaml = scF.read()
            setInDict(pages, pl, name, filename, ext, scYaml)
    return pages
