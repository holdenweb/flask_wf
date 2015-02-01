#!python

"""This fabfile is intended to allow the easy creation of Flask web sites
on Web Faction servers. So far it is purely for personal use only.
"""
import posixpath

from fabric.api import run, local, abort, env, get, put, task
from fabric.contrib.files import exists
from fabric.context_managers import cd, lcd, settings, hide

from credentials import username, password

# Set system parameters
# Python version
PYTHON_BIN = "python2.7"
PYTHON_PREFIX = "/usr/local" # e.g. /usr/local  Use "" for automatic
PYTHON_FULL_PATH = "%s/bin/%s" % (PYTHON_PREFIX, PYTHON_BIN) if PYTHON_PREFIX else PYTHON_BIN

# Set basic application parameters
USER = username
PASSWD = password
HOST = 'web105.webfaction.com'
SITENAME = "holdenweb_preview"
APPNAME = "new_app_7"
APP_NAME = APPNAME
APP_PORT = 30123 # Should read port from WebFaction API
URLPATH = "/"

PROJECT_DIR = posixpath.join('/home', USER, 'webapps', APP_NAME)
VENV_SUBDIR = 'venv'
VENV_DIR = posixpath.join(PROJECT_DIR, VENV_SUBDIR)
SRC_SUBDIR = 'app'
SRC_DIR = posixpath.join(PROJECT_DIR, SRC_SUBDIR)

# Extract some parameters from the environment?

# Establish universal fabric environment parameters
# Host and login username:
env.hosts = ['%s@%s' % (USER, HOST)]

@task
def server_stop():
    with cd(PROJECT_DIR):
        run("apache2/bin/stop")

@task
def server_start():
    with cd(PROJECT_DIR):
        run("apache2/bin/start")

@task
def server_restart():
    with cd(PROJECT_DIR):
        run("apache2/bin/restart")

def install_dependencies():
    ensure_virtualenv()
    with virtualenv(VENV_DIR):
        with cd(SRC_DIR):
            run_venv("pip install -r requirements.txt")

def virtualenv(venv_dir):
    """
    Context manager that establishes a virtualenv to use.
    """
    return settings(venv=venv_dir)


def run_venv(command, **kwargs):
    """
    Runs a command in a virtualenv (which has been specified using
    the virtualenv context manager
    """
    run("source %s/bin/activate" % env.venv + " && " + command, **kwargs)

@task
def ensure_virtualenv():
    if exists(VENV_DIR):
        return
    with cd(PROJECT_DIR):
        run("virtualenv --no-site-packages --python=%s %s" %
            (PYTHON_BIN, VENV_SUBDIR))
        with virtualenv(VENV_DIR):
            run("echo %s > %s/lib/%s/site-packages/projectsource.pth" %
                (SRC_DIR, VENV_SUBDIR, PYTHON_BIN))
            run_venv("pip install -r {}/requirements.txt".format(SRC_SUBDIR))

def ensure_src_dir():
    if not exists(SRC_DIR):
        local("git clean -fX")
        put(SRC_SUBDIR, PROJECT_DIR)

WF_SERVR = WF_SESSN = WF_ACCNT = None

def auth_webfaction():
    """Authenticates one-time with the Web Faction server.
    The shenanigans with the globals are to hide xmlrpclib
    from fabric's task discovery logic, which apparently
    does something nasty like try an equality test that then
    triggers an exception. Which I can do without. Sorry."""
    global WF_SERVR, WF_SESSN, WF_ACCNT
    if not WF_SERVR:
        from xmlrpclib import ServerProxy
        server = ServerProxy('https://api.webfaction.com/')
        session_id, account = server.login(USER, PASSWD)
        WF_SERVR, WF_SESSN, WF_ACCNT = server, session_id, account

@task
def app_create():
    auth_webfaction()
    WF_SERVR.create_app(WF_SESSN, APP_NAME, "mod_wsgi428-python27")
    # The above automatically creates $PROJECT_DIR
    app = [a for a in WF_SERVR.list_apps(WF_SESSN) if a['name'] == APP_NAME][0]
    print "Creating application", app
    #websites = WF_SERVR.list_websites(WF_SESSN)
    #website = [w for w in websites if w['name'] == SITENAME][0]
    #print "Your current site:", website
    ensure_src_dir()
    ensure_virtualenv()
    print "SRC_SUBDIR is", SRC_SUBDIR
    with cd(PROJECT_DIR):
        with virtualenv(VENV_DIR):
            run("""\
echo "import sys
sys.path.insert(0, '{}')
from app import app as application" >> wsgi.py""".format(PROJECT_DIR))
            local("echo Remember to fix up httpd.conf")
            #get("apache2/conf/httpd.conf", "httpd.conf.%(host)s")
            #filename = "httpd.conf.%s" % env.host_string
            #text = open(filename).readlines()
            #py_home =  "WSGIPythonHome {}/bin\n".format(VENV_DIR)
            #for i in range(len(text)):
                #if text[i].startswith("WSGI"):
                    #text.insert(i, py_home)
                    #break
            #for i in range(len(text)):
                #if text[i].strip().startswith("AddHandler"):
                    #text.insert(i, """\
    #RewriteEngine on
    #RewriteBase /
    #WSGIScriptReloading On
#""")
                    #break
        #outf = open(filename, "w")
        #outf.write("".join(text))
        #outf.close()
        #put(filename, PROJECT_DIR+"/apache2/conf/httpd.conf")
        run("apache2/bin/restart")
    
@task
def py_version():
    with virtualenv(VENV_DIR):
        run_venv("which python; which pip")

@task
def app_delete():
    server_stop()
    auth_webfaction()
    WF_SERVR.delete_app(WF_SESSN, APP_NAME)

@task
def domain_list():
    auth_webfaction()
    domains = WF_SERVR.list_domains(WF_SESSN)
    for d in domains:
        print d

@task
def app_list():
    auth_webfaction()
    apps = WF_SERVR.list_apps(WF_SESSN)
    for app in apps:
        print app

@task
def domain_list():
    auth_webfaction()
    domains = WF_SERVR.list_domains(WF_SESSN)
    for domain in domains:
        print domain

## Step 2
## deploy the app
#cd $HOME
#easy_install-2.7 flask
#mkdir $HOME/webapps/$APPNAME/$APPNAME
#touch $HOME/webapps/$APPNAME/$APPNAME/__init__.py
#touch $HOME/webapps/$APPNAME/$APPNAME/index.py
#echo "import sys" > $HOME/webapps/$APPNAME/wsgi.py
#echo "sys.path.insert(0, '$HOME/webapps/$APPNAME')" >> $HOME/webapps/$APPNAME/wsgi.py
#echo -e "from $APPNAME import app as application\n" >> $HOME/webapps/$APPNAME/wsgi.py
#sed -i "s^WSGILazyInitialization On^WSGILazyInitialization On\nWSGIScriptAlias / $HOME/webapps/
#$APPNAME/wsgi.py^" $HOME/webapps/$APPNAME/apache2/conf/httpd.conf
#sed -i "s^AddHandler wsgi-script .py^AddHandler wsgi-script .py\n    RewriteEngine on\n    Rewr
#iteBase /\n    WSGIScriptReloading On^" $HOME/webapps/$APPNAME/apache2/conf/httpd.conf
#sed -i "s/htdocs/$APPNAME/g" $HOME/webapps/$APPNAME/apache2/conf/httpd.conf

#cat << EOF >> $HOME/webapps/$APPNAME/$APPNAME/__init__.py
#from flask import Flask
#app = Flask(__name__)

#EOF

#if [[ "$URLPATH" != "/" ]]; then
#cat << EOF >> $HOME/webapps/$APPNAME/$APPNAME/__init__.py
#class WebFactionMiddleware(object):
    #def __init__(self, app):
        #self.app = app
    #def __call__(self, environ, start_response):
        #environ['SCRIPT_NAME'] = '$URLPATH'
        #return self.app(environ, start_response)

#app.wsgi_app = WebFactionMiddleware(app.wsgi_app)

#EOF
#fi

#cat << EOF >> $HOME/webapps/$APPNAME/$APPNAME/__init__.py
#@app.route("/")
#def hello():
    #return "Hello World!"

#if __name__ == "__main__":
    #app.run()
#EOF

## Step 3
#$HOME/webapps/$APPNAME/apache2/bin/restart

# First of all we need to create a new application to support the web site

@task
def create_app(name):
    pass