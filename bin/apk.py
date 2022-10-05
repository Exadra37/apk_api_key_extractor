#!/usr/bin/python3

# I don't believe in license.
# You can do whatever you want with this program.

import argparse
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

from colored import attr, bg, fg

t_templates = [
    '_report.html',
]
t_templates_str = {}

############################### FUNCTIONS ###############################
def loadTemplates():
    for tpl in t_templates:
        t_templates_str[tpl] = 'aaa'
    print(t_templates_str)

# loadTemplates()
# exit()


def format_bytes( size ):
    units = ['b', 'kb', 'mb', 'gb', 'tb']
    i = 0
    while size>=1024 and i<4:
        size = size / 1024
        i = i + 1
    return str(round(size,2)) + units[i]

def printH1( title ):
    sys.stdout.write( '\n\n%s### %s ###%s\n\n' % (fg('light_cyan'),title,attr(0)) )

def printH2( title ):
    sys.stdout.write( '\n%s# %s #%s\n\n' % (fg('light_blue'),title,attr(0)) )

def _print( txt, extra='', level='normal' ):
    if not len(level):
        level = 'normal'
    t_colors = {
        'silent': 'grey_35',
        'hsilent': 'grey_35',
        'debug': 'light_magenta',
        'hdebug': 'magenta',
        'normal': 'white',
        'hnormal': 'light_gray',
        'info': 'light_green',
        'hinfo': 'green',
        'notice': 'gold_1',
        'hnotice': 'dark_orange_3a',
        'warning': 'light_red',
        'hwarning': 'red',
    }
    if len(txt):
        sys.stdout.write( '%s%s' % (fg(t_colors[level]),txt) )
        if len(extra):
            # sys.stdout.write( ' [%s:%s]' % (level.replace('h',''),extra) )
            sys.stdout.write( ' -- %s' % (extra) )
        sys.stdout.write( '%s\n' % attr(0) )
############################### FUNCTIONS ###############################


############################### BASIC INFOS ###############################
def readInfos( grep_term ):
    printH1( 'INFOS' )

    _print( ('Package: %s' % root.attrib['package']) )

    if 'platformBuildVersionCode' in root.attrib:
        version = root.attrib['platformBuildVersionCode']
    elif 'compileSdkVersion' in root.attrib:
        version = root.attrib['compileSdkVersion']
    else:
        version = '?'
    _print( ('Build: %s' % version) )

    if not grep_term:
        grep_term = root.attrib['package'].split('.')[1]
    _print( ('Grep term: %s' % grep_term) )
    # sys.stdout.write( '\n\n' )

    return grep_term
############################### BASIC INFOS ###############################


############################### PERMISSIONS ###############################
def listPermissionsCreated():
    t_term = []
    t_noterm = []
    t_all = root.findall('permission')
    for obj in t_all:
        if grep_term in obj.attrib['name']:
            t_term.append( obj )
        else:
            t_noterm.append( obj )

    printH2( 'PERMISSIONS CREATED (<permission>) (%d)' % len(t_all) )
    printPermissionsCreated( t_term )
    if len(t_term) and len(t_noterm):
        sys.stdout.write( '---\n' )
    printPermissionsCreated( t_noterm, 'h' )

def printPermissionsCreated( tab, plevel0='' ):
    t_warning = {'EXTERNAL_STORAGE':'external storage permission','INTERNET':'webview permission'}
    for obj in tab:
        extra = ''
        plevel = 'normal'
        for k,v in t_warning.items():
            if k in obj.attrib['name']:
                extra = v
                plevel = 'warning'
        if not 'protectionLevel' in obj.attrib or obj.attrib['protectionLevel'] != 'signature':
            extra = 'no signature'
            plevel = 'warning'
        _print( obj.attrib['name'], extra, plevel0+plevel )


def listPermissionsUsed():
    t_term = []
    t_noterm = []
    t_all = root.findall('uses-permission')
    for obj in t_all:
        if grep_term in obj.attrib['name']:
            t_term.append( obj )
        else:
            t_noterm.append( obj )

    printH2( 'PERMISSIONS USED (<uses-permission>) (%d)' % len(t_all) )
    printPermissionsUsed( t_term )
    if len(t_term) and len(t_noterm):
        sys.stdout.write( '---\n' )
    printPermissionsUsed( t_noterm, 'h' )

def printPermissionsUsed( tab, plevel0='' ):
    t_warning = {'EXTERNAL_STORAGE':'external storage permission','INTERNET':'webview permission'}
    for obj in tab:
        extra = ''
        plevel = 'normal'
        for k,v in t_warning.items():
            if k in obj.attrib['name']:
                extra = v
                plevel = 'warning'
        _print( obj.attrib['name'], extra, plevel0+plevel )


def listPermissionsRequired():
    t_all = root.findall('permission')
    t_term = []
    t_noterm = []
    for elem in root.iter():
        if 'permission' in elem.attrib:
            if grep_term in elem.attrib['permission']:
                t_term.append( elem )
            else:
                t_noterm.append( elem )

    printH2( 'PERMISSIONS REQUIRED (permission="") (%d)' % (len(t_term)+len(t_noterm)) )
    printPermissionsRequired( t_all, t_term )
    if len(t_term) and len(t_noterm):
        sys.stdout.write( '---\n' )
    printPermissionsRequired( t_all, t_noterm, 'h' )

def printPermissionsRequired( t_allperm, tab, plevel0='' ):
    t_unwarn = ['android.permission','com.google.android','com.google.firebase']
    for obj in tab:
        extra = 'permission used but not created'
        plevel = 'warning'
        for perm in t_allperm:
            if obj.attrib['permission'] == perm.attrib['name']:
                extra = ''
                plevel = 'normal'
            for w in t_unwarn:
                if w in obj.attrib['permission']:
                    extra = ''
                    plevel = 'normal'
        _print( obj.attrib['permission'], extra, plevel0+plevel )
        # sys.stdout.write( '%s%s %s%s\n' % (fg(color),obj.attrib['permission'],extra,attr(0)) )

def listPermissions():
    printH1( 'PERMISSIONS' )
    listPermissionsCreated()
    listPermissionsUsed()
    listPermissionsRequired()
############################### PERMISSIONS ###############################


############################### ACTIVITIES ###############################
def listActivities():
    app = root.find( 'application' )
    t_all = app.findall('activity')
    t_all = t_all + app.findall('activity-alias')
    t_term = []
    t_noterm = []
    for obj in t_all:
        if grep_term in obj.attrib['name']:
            t_term.append( obj )
        else:
            t_noterm.append( obj )
    printH1( 'ACTIVITIES (%d)' % len(t_all) )
    printActivities( t_term )
    if len(t_term) and len(t_noterm):
        sys.stdout.write( '---\n' )
    printActivities( t_noterm, 'h' )

def printActivities( tab, plevel0='' ):
    for obj in tab:
        if 'exported' in obj.attrib:
            extra = 'exported param'
            exported = obj.attrib['exported'].lower()
        elif obj.findall('intent-filter'):
            extra = 'intent-filter'
            exported = 'true'
        else:
            exported = 'false'
        if 'permission' in obj.attrib and grep_term in obj.attrib['permission']:
            exported = 'false'
        if exported == 'false':
            extra = ''
            plevel = 'normal'
        else:
            extra = "activity is exported ("+extra+") and no '" + grep_term + "' permission setted"
            plevel = 'warning'
            if 'enabled' in obj.attrib and obj.attrib['enabled'].lower() == 'false':
                extra = extra + " but is disabled"
                plevel = 'notice'
        _print( '[+] '+obj.attrib['name'] ,extra, plevel0+plevel )
        for k,v in sorted(obj.attrib.items()):
            k = k.replace('','')
            if not k == 'name':
                _print( '      %s: %s' % (k,v) ,'', plevel0+plevel )
        if display_commands:
            # t_actions = ['android.intent.action.VIEW']
            # if obj.findall('intent-filter'):
            #     for intentfilter in obj.findall('intent-filter'):
            #         if intentfilter.findall('action'):
            #             for action in intentfilter.findall('action'):
            #                 if not action.attrib['name'] in t_actions:
            #                     t_actions.append( action.attrib['name'] )
            # for action in t_actions:
                # _print( '      adb shell am start -S -a '+action+' -n '+root.attrib['package']+'/'+obj.attrib['name'] ,'', 'silent' )
            _print( '      adb shell am start -S -n '+root.attrib['package']+'/'+obj.attrib['name'], '', 'silent' )
############################### ACTIVITIES ###############################


############################### SERVICES ###############################
def listServices():
    app = root.find( 'application' )
    t_all = app.findall('service')
    t_term = []
    t_noterm = []
    for obj in t_all:
        if grep_term in obj.attrib['name']:
            t_term.append( obj )
        else:
            t_noterm.append( obj )
    printH1( 'SERVICES (%d)' % len(t_all) )
    printServices( t_term )
    if len(t_term) and len(t_noterm):
        sys.stdout.write( '---\n' )
    printServices( t_noterm, 'h' )


def printServices( tab, plevel0='' ):
    for obj in tab:
        if 'exported' in obj.attrib:
            extra = 'exported param'
            exported = obj.attrib['exported'].lower()
        elif obj.findall('intent-filter'):
            extra = 'intent-filter'
            exported = 'true'
        else:
            exported = 'false'
        if 'permission' in obj.attrib and grep_term in obj.attrib['permission']:
            exported = 'false'
        if exported == 'false':
            extra = ''
            plevel = 'normal'
        else:
            extra = "service is exported ("+extra+") and no '" + grep_term + "' permission setted"
            plevel = 'warning'
            if 'enabled' in obj.attrib and obj.attrib['enabled'].lower() == 'false':
                extra = extra + " but is disabled"
                plevel = 'notice'
        _print( '[+] '+obj.attrib['name'] ,extra, plevel0+plevel )
        for k,v in sorted(obj.attrib.items()):
            k = k.replace('','')
            if not k == 'name':
                _print( '      %s: %s' % (k,v) ,'', plevel0+plevel )
        if display_commands:
            _print( '      adb shell am startservice -n '+root.attrib['package']+'/'+obj.attrib['name'],'', 'silent' )
############################### SERVICES ###############################


############################### RECEIVERS ###############################
def listReceivers():
    app = root.find( 'application' )
    t_all = app.findall('receiver')
    t_term = []
    t_noterm = []
    for obj in t_all:
        if grep_term in obj.attrib['name']:
            t_term.append( obj )
        else:
            t_noterm.append( obj )
    printH1( 'RECEIVERS (%d)' % len(t_all) )
    printReceivers( t_term )
    if len(t_term) and len(t_noterm):
        sys.stdout.write( '---\n' )
    printReceivers( t_noterm, 'h' )


def printReceivers( tab, plevel0='' ):
    for obj in tab:
        if 'exported' in obj.attrib:
            extra = 'exported param'
            exported = obj.attrib['exported'].lower()
        elif obj.findall('intent-filter'):
            extra = 'intent-filter'
            exported = 'true'
        else:
            exported = 'false'
        if 'permission' in obj.attrib and grep_term in obj.attrib['permission']:
            exported = 'false'
        if exported == 'false':
            extra = ''
            plevel = 'normal'
        else:
            extra = "receiver is exported ("+extra+") and no '" + grep_term + "' permission setted"
            plevel = 'warning'
            if 'enabled' in obj.attrib and obj.attrib['enabled'].lower() == 'false':
                extra = extra + " but is disabled"
                plevel = 'notice'
        _print( '[+] '+obj.attrib['name'] ,extra, plevel0+plevel )
        for k,v in sorted(obj.attrib.items()):
            k = k.replace('','')
            if not k == 'name':
                _print( '      %s: %s' % (k,v) ,'', plevel0+plevel )
        if display_commands:
            # t_actions = ['android.intent.action.VIEW']
            # if obj.findall('intent-filter'):
            #     for intentfilter in obj.findall('intent-filter'):
            #         if intentfilter.findall('action'):
            #             for action in intentfilter.findall('action'):
            #                 if not action.attrib['name'] in t_actions:
            #                     t_actions.append( action.attrib['name'] )
            # for action in t_actions:
                # _print( '      adb shell am start -S -a '+action+' -n '+root.attrib['package']+'/'+obj.attrib['name'] ,'', 'silent' )
            _print( '      adb shell am broadcast -n '+root.attrib['package']+'/'+obj.attrib['name'], '', 'silent' )
############################### RECEIVERS ###############################


############################### PROVIDERS ###############################
def listProviders():
    app = root.find( 'application' )
    t_all = app.findall('provider')
    t_term = []
    t_noterm = []
    t_providers_uri = {}
    for obj in t_all:
        if obj.attrib['authorities'].startswith('@'):
            continue
        if grep_term in obj.attrib['authorities']:
            t_term.append( obj )
        else:
            t_noterm.append( obj )
        t_providers_uri[ obj.attrib['authorities'] ] = getProviderURI( obj.attrib['authorities'] )
    printH1( 'PROVIDERS (%d)' % len(t_all) )
    printProviders( t_term, t_providers_uri )
    if len(t_term) and len(t_noterm):
        sys.stdout.write( '---\n' )
    printProviders( t_noterm, t_providers_uri, 'h' )

def getProviderURI( authority ):
    t_uri = [ 'content://'+authority ]
    # t_uri = [ 'content://'+authority ]
    cmd = 'egrep -hro "content://'+ authority + '[a-zA-Z0-9_-/\.]+" "' + src_directory + '/smali/" 2>/dev/null'
    # print(cmd)
    try:
        output = subprocess.check_output( cmd, shell=True ).decode('utf-8')
        # print(output)
    except Exception as e:
        # sys.stdout.write( "%s[-] error occurred: %s%s\n" % (fg('red'),e,attr(0)) )
        return t_uri

    for l in output.split("\n"):
        if not len(l):
            continue
        tiktok = ''
        l = l.strip().strip('/').replace( 'content://','' )
        t_split = l.split('/')
        for token in t_split:
            tiktok = tiktok + '/' + token
            tiktok = tiktok.strip('/')
            uri1 = 'content://' + tiktok
            if not uri1 in t_uri:
                t_uri.append( uri1 )
            # uri2 = 'content://' + tiktok + '/'
            # if not uri2 in t_uri:
            #     t_uri.append( uri2 )

    return t_uri


def printProviders( tab, t_providers_uri, plevel0='' ):
    for obj in tab:
        if 'exported' in obj.attrib:
            extra = 'exported param'
            exported = obj.attrib['exported'].lower()
        elif obj.findall('intent-filter'):
            extra = 'intent-filter'
            exported = 'true'
        else:
            exported = 'false'
        if ('permission' in obj.attrib and grep_term in obj.attrib['permission']) or ('readPermission' in obj.attrib and grep_term in obj.attrib['readPermission']):
            exported = 'false'
        if exported == 'false':
            extra = ''
            plevel = 'normal'
        else:
            extra = "provider is exported ("+extra+") and no '" + grep_term + "' permission setted"
            plevel = 'warning'
            if 'enabled' in obj.attrib and obj.attrib['enabled'].lower() == 'false':
                extra = extra + " but is disabled"
                plevel = 'notice'
        _print( '[+] '+obj.attrib['authorities'] ,extra, plevel0+plevel )
        for k,v in sorted(obj.attrib.items()):
            k = k.replace('','')
            if not k == 'name':
                _print( '      %s: %s' % (k,v) ,'', plevel0+plevel )
        if obj.attrib['authorities'] in t_providers_uri and len(t_providers_uri[obj.attrib['authorities']]):
            if len(obj.attrib)>1:
                _print( '      ---', '', plevel0+plevel )
            for uri in sorted(t_providers_uri[obj.attrib['authorities']]):
                _print( '      %s' % uri, '', plevel0+plevel )
                if display_commands:
                    _print( '      adb shell content query --uri '+uri, '', 'silent' )
############################### PROVIDERS ###############################


############################### INTERESTING FILES ###############################
t_files_warning = ['conf','secret','pass','key','auth','cer','crt']
t_files_ignore = ['.shader','.dict','abp.txt','crashlytics-build.properties','tzdb.dat','.snsr','.alyp','.alyg','.frag','.vert','.gmt','.kml','.traineddata','.glsl','.glb','.css','.otf','.aac','.mid','.ogg','.m4a','.m4v','.ico','.gif','.jpg','.jpeg','.png','.bmp','.svg','.avi','.mpg','.mpeg','.mp3','.woff','.woff2','.ttf','.eot','.mp3','.mp4','.wav','.mpg','.mpeg','.avi','.mov','.wmv' ]

def _listFiles( dir ):
    t_all = []
    t_files = []

    # r=root, d=directories, f=files
    for r, d, f in os.walk( dir ):
        for file in f:
            filepath = os.path.join(r,file)
            # filename = filepath.replace(src_directory+'/','')
            filename = filepath.replace(' ','\ ')
            filesstats = os.stat( filepath )
            filesize = format_bytes( filesstats.st_size )
            t_all.append( {'filename':filename,'filesize':filesize} )
            if not filesstats.st_size:
                ignore = True
            else:
                ignore = False
                for i in t_files_ignore:
                    if i in filename.lower():
                        ignore = True
            if not ignore:
                t_files.append( {'filename':filename,'filesize':filesize} )

    return t_all,t_files


def printFiles( t_files ):
    for file in sorted(t_files,key=lambda k:k['filename']):
        extra = ''
        plevel = 'normal'
        for w in t_files_warning:
            if w in file['filename'].lower():
                extra = 'can be a sensitive file (\'' + w + '\' found in filemane)'
                plevel = 'warning'
        # sys.stdout.write( '%s%s (%s) %s%s\n' % (fg(color),file['filename'],file['filesize'],extra,attr(0)) )
        _print( '%s (%s)' % (file['filename'],file['filesize']), extra, plevel )


def listFiles():
    printH1( 'FILES' )
    t_all, t_files = _listFiles( src_directory+'/assets/' )
    printH2( 'ASSETS (%d/%d)' % (len(t_files),len(t_all)) )
    printFiles( t_files )
    t_all, t_files = _listFiles( src_directory+'/res/raw/' )
    printH2( 'RES/RAW (%d/%d)' % (len(t_files),len(t_all)) )
    printFiles( t_files )
############################### INTERESTING FILES ###############################


############################### DEEP LINKS ###############################
def listDeepLinks():
    app = root.find( 'application' )
    t_items = app.findall('activity')
    t_items = t_items + app.findall('service')
    t_deeplinks = []
    for activity in t_items:
        t_filters = activity.findall('intent-filter')
        if not t_filters:
            pass
        for filter in t_filters:
            t_tmpdl = []
            has_action = False
            has_category = False
            for child in filter:
                if child.tag == 'action' and child.attrib['name'] == 'android.intent.action.VIEW':
                    has_action = True
                if child.tag == 'category' and child.attrib['name'] == 'android.intent.category.BROWSABLE':
                    has_category = True
                if child.tag == 'data': # and 'scheme' in child.attrib:
                    t_tmpdl.append( child )
            # if has_action and has_category:
            t_deeplinks.extend( t_tmpdl )

    printH1( 'DEEP LINKS (%d)' % (len(t_deeplinks)) )

    for deeplink in t_deeplinks:
        sys.stdout.write( '<data ' )
        for k,v in deeplink.items():
            # sys.stdout.write( 'android:%s="%s" ' % (k,v) )
            sys.stdout.write( '%s="%s" ' % (k,v) )
        sys.stdout.write( '/>\n' )
############################### DEEP LINKS ###############################


parser = argparse.ArgumentParser()
parser.add_argument( "-d","--directory",help="source directory" )
parser.add_argument( "-t","--term",help="term referencing the editor" )
parser.add_argument( "-c","--command",help="display commands to run", action="store_true" )
parser.add_argument( "-m","--mod",help="mod to run" )
parser.parse_args()
args = parser.parse_args()

if args.term:
    grep_term = args.term
else:
    grep_term = ''

if args.mod:
    mod = args.mod
else:
    mod = 'paroslf'

if args.command:
    display_commands = True
else:
    display_commands = False

if not args.directory:
    parser.error( 'source directory is missing' )

args.directory = args.directory.rstrip('/')
src_directory = args.directory
if not os.path.isdir(src_directory):
    parser.error( 'source directory not found' )

src_manifest = src_directory + '/' + 'AndroidManifest.xml'
if not os.path.isfile(src_manifest):
    parser.error( 'Manifest file not found' )

try:
    etparse = ET.parse( src_manifest )
except:
    parser.error( 'Cannot read Manifest' )

root = etparse.getroot()
if not root:
    parser.error( 'Cannot read Manifest' )

for elem in root.iter():
    # print( elem.attrib )
    elem.attrib = { k.replace('{http://schemas.android.com/apk/res/android}', ''): v for k, v in elem.attrib.items() }
    # print( elem.attrib )

grep_term = readInfos( grep_term )

for m in mod:
    if m == 'p':
        listPermissions()
    elif m == 'f':
        listFiles()
        # listAssets()
        # listRaw()
    elif m == 'a':
        listActivities()
    elif m == 'r':
        listReceivers()
    elif m == 'o':
        listProviders()
    elif m == 's':
        listServices()
    elif m == 'l':
        listDeepLinks()
