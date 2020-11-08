from time import time
import os, subprocess, shutil, jinja2, tarfile, re
from zipfile import ZipFile
from json import load, dump
class Configuration(object):
    def __init__(self, directory):
        self.package = "com.Rosehip.myapp"
        self.name = "Rosehip"
        self.icon_name = "Rosehip"  
        self.version = "1.0.0"
        self.numeric_version = "1"
        self.orientation = "sensorLandscape"
        self.permissions = ["INTERNET"]        
        self.include_pil = True
        self.include_sqlite = False
        self.layout = "internal"
        self.source = False
        self.expansion = True
        self.targetsdk = 26
        try: self.__dict__.update(load(open(r"Rosehip\.android.json", "r")))
        except: pass
    def save(self, directory): dump(self.__dict__, open(r"Rosehip\.android.json", "w"))
class PatternList(object):
    def __init__(self, *args):
        self.patterns = [ ]
        for i in args: self.load(i)
    def match(self, s): return any([p.match(s) or p.match("/" + s) for p in self.patterns])
    def load(self, fn):
        with open(fn, "r") as f:
            for l in f:
                l = l.strip()
                if l and not l.startswith("#"): self.patterns.append(self.compile(l))
    def compile(self, pattern):
        regexp = ""
        while pattern:
            if pattern.startswith("**"):
                regexp += r'.*'
                pattern = pattern[2:]
            elif pattern[0] == "*":
                regexp += r'[^/]*'
                pattern = pattern[1:]
            elif pattern[0] == '[':
                regexp += r'['
                pattern = pattern[1:]
                while pattern and pattern[0] != ']':
                    regexp += pattern[0]
                    pattern = pattern[1:]
                pattern = pattern[1:]
                regexp += ']'
            else:
                regexp += re.escape(pattern[0])
                pattern = pattern[1:]  
        regexp += "$"
        return re.compile(regexp, re.I)
def join_and_check(base, sub):return os.path.join(base, sub) if os.path.exists(os.path.join(base, sub)) else None
def make_tar(fn, source_dirs):
    def include(fn): return not blacklist.match(fn) or whitelist.match(fn)
    tf = tarfile.open(fn, "w:gz")
    added = set()
    def add(fn, relfn):
        adds = [ ]
        while relfn:
            adds.append((fn, relfn))
            fn = os.path.dirname(fn)
            relfn = os.path.dirname(relfn)
        adds.reverse()
        for fn, relfn in adds:
            if relfn not in added:
                added.add(relfn)
                tf.add(fn, relfn, recursive=False)
    for sd in source_dirs:
        sd = os.path.abspath(sd)    
        for dir, dirs, files in os.walk(sd):
            for _fn in dirs:
                fn = os.path.join(dir, _fn)
                relfn = os.path.relpath(fn, sd)
                if include(relfn):add(fn, relfn)
            for fn in files:        
                fn = os.path.join(dir, fn)
                relfn = os.path.relpath(fn, sd)
                if include(relfn):add(fn, relfn)
    tf.close()
def edit_file(fn, pattern, line):
    lines = [ ]
    for l in open(fn, "r"): #.read()
        if re.match(pattern, l):
            l = line + "\n"
        lines.append(l)
    open(fn, "w").write(''.join(lines))
def zip_directory(zf, dirname):
    for dirname, dirs, files in os.walk(dirname):
        for fn in files:
            fn = os.path.join(dirname, fn)
            zf.write(fn)
def make_tree(src, dest):
    def ignore(dir, files):
        rv = [ ]
        for basename in files:
            fn = os.path.join(dir, basename)
            relfn = os.path.relpath(fn, src)
            ignore = False
            if blacklist.match(relfn):ignore = True
            if whitelist.match(relfn):ignore = False
            if ignore:rv.append(basename)
        return rv
    shutil.copytree(src, dest, ignore=ignore)
environment = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
def render(template, dest, **kwargs):open(dest, "wb").write(environment.get_template(template).render(**kwargs).encode("utf-8"))
config = Configuration("Rosehip")
blacklist = PatternList("blacklist.txt")
whitelist = PatternList("whitelist.txt")
manifest_extra = ""
default_icon = "templates/pygame-icon.png"
default_icon_fg = "templates/pygame-icon-foreground.png"
default_icon_bg = "templates/pygame-icon-background.png"
default_presplash = "templates/pygame-presplash.jpg"
private_dir = "Rosehip"
public_dir = None
assets_dir = None
versioned_name = config.name.replace(" ", "").replace("'", "") + "-" + config.version
config.name = config.name.replace("'", "\\'")
config.icon_name = config.icon_name.replace("'", "\\'")
private_version = str(time())
public_version = None
render("AndroidManifest.tmpl.xml","AndroidManifest.xml", config = config, manifest_extra = manifest_extra,)
render("strings.xml","res/values/strings.xml",public_version = public_version,private_version = private_version,config = config)
try:os.unlink("build.xml")
except:pass
subprocess.call(["android-sdk\\tools\\android.bat", "update", "project", "-p", '.', '-t', 'android-28', '-n', versioned_name,])
if os.path.isdir("assets"):shutil.rmtree("assets")
if assets_dir is not None:make_tree(assets_dir, "assets")
else:os.mkdir("assets")
if os.path.exists("renpy/common"):
    if os.path.isdir("assets/common"):shutil.rmtree("assets/common")
    make_tree("renpy/common", "assets/common")
    for dirpath, dirnames, filenames in os.walk("assets", topdown=False):
        for fn in filenames + dirnames:
            if fn[0] != ".": os.rename(os.path.join(dirpath, fn), os.path.join(dirpath, "x-" + fn))
expansion_file = "main.{}.{}.obb".format(config.numeric_version, config.package)
zf = ZipFile(expansion_file, "w", 0)
zip_directory(zf, "assets")
zf.close()
shutil.rmtree("assets")
os.mkdir("assets")
file_size = os.path.getsize(expansion_file)
edit_file("src/org/renpy/android/DownloaderActivity.java",r'    private int fileVersion =','    private int fileVersion = {};'.format(config.numeric_version))
edit_file("src/org/renpy/android/DownloaderActivity.java",r'    private int fileSize =','    private int fileSize = {};'.format(file_size))
private_dirs = ['private', private_dir]
if os.path.exists("engine-private"):private_dirs.append("engine-private")
make_tar("assets/private.mp3", private_dirs)
if public_dir is not None:make_tar("assets/public.mp3", [ public_dir ])
shutil.copy(join_and_check("Rosehip", "android-icon.png") or default_icon, "res/mipmap-xxhdpi/ic_launcher.png")
shutil.copy(join_and_check("Rosehip", "android-icon-foreground.png") or default_icon_fg, "res/drawable-xxhdpi/ic_foreground.png")
shutil.copy(join_and_check("Rosehip", "android-icon-background.png") or default_icon_bg, "res/drawable-xxhdpi/ic_background.png")
shutil.copy(join_and_check("Rosehip", "android-presplash.jpg") or default_presplash, "res/drawable-xxhdpi/presplash.jpg")
try:subprocess.check_call(["apache-ant\\bin\\ant.bat", "clean", "release", "install"])
except: pass
if expansion_file is not None:
    dest = f"/mnt/sdcard/{expansion_file}"
    subprocess.check_call(["android-sdk\\platform-tools\\adb.exe", "push", expansion_file, dest ])
    os.rename(expansion_file, "bin/" + expansion_file)
subprocess.check_call(["android-sdk\\platform-tools\\adb.exe", "shell","am", "start","-W","-a", "android.intent.action.MAIN","{}/org.renpy.android.{}".format(config.package, "PythonActivity"),])
