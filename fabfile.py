#!python

"""This fabfile is intended to allow the easy creation of Flask web sites
on Web Faction servers. So far it is purely for personal use only.
"""
import posixpath
import subprocess
from cStringIO import StringIO

from fabric.api import run, local, abort, env, get, put, task
from fabric.contrib.files import exists
from fabric.context_managers import cd, lcd, settings, hide
from jinja2 import Template

from credentials import username, password

APPNAME = "new_app_8"

############################################################################
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
APP_NAME = APPNAME
APP_TYPE = "custom_websockets_app_with_port"
APP_PORT = None # Should read port from created WebFaction app detsails
URLPATH = "/"

PROJECT_DIR = posixpath.join('/home', USER, 'webapps', APP_NAME)
VENV_SUBDIR = 'venv'
VENV_DIR = posixpath.join(PROJECT_DIR, VENV_SUBDIR)
SRC_SUBDIR = 'htdocs'
SRC_DIR = posixpath.join(PROJECT_DIR, SRC_SUBDIR)

# Extract some parameters from the environment?
############################################################################

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
        with cd(PROJECT_DIR):
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
    print "Creating application", WF_SESSN, APP_NAME, APP_TYPE
    WF_SERVR.create_app(WF_SESSN, APP_NAME, APP_TYPE)
    # The above automat,kl8ically creates $PROJECT_DIR
    app = [a for a in WF_SERVR.list_apps(WF_SESSN) if a['name'] == APP_NAME][0]
    SOCKET = app["port"]
    print "Created application:", app
    #websites = WF_SERVR.list_websites(WF_SESSN)
    #website = [w for w in websites if w['name'] == SITENAME][0]
    #print "Your current site:", website
    ensure_src_dir()
    print "SRC_SUBDIR is", SRC_SUBDIR
    ensure_virtualenv()
    print "Virtual environment is", VENV_DIR
    put("requirements.txt", PROJECT_DIR)
    install_dependencies()
    render_context = {
        "APP_NAME": APP_NAME,
        "SOCKET": SOCKET,
    }
    with cd(PROJECT_DIR), virtualenv(VENV_DIR):
        print "Local directory in subprocess:", subprocess.check_output("pwd")        
        put("apache2.tgz", PROJECT_DIR)
        run("tar xzvf apache2.tgz")
        run("rm apache2/logs/httpd.pid") # remove when tar file patched
        run("rm apache2.tgz")
        conf_files = subprocess.check_output("find apache2 -type f".split()).splitlines()
        for filename in conf_files:
            template = Template(open(filename).read())
            rendered = template.render(render_context)
            put(StringIO(rendered.encode("Latin-1")), filename)
        run("chmod u+x apache2/bin/*")
        run("apache2/bin/start")
    
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

@task
def site_list():
    auth_webfaction()
    websites = WF_SERVR.list_websites(WF_SESSN)
    for site in websites:
        print site
