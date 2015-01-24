#!python

"""This fabfile is intended to allow the easy creation of Flask web sites
on Web Faction servers. So far it is purely for personal use only.
"""

import posixpath

from credentials import username, password
from fabric.api import run, local, abort, env, put, task
from fabric.contrib.files import exists
from fabric.context_managers import cd, lcd, settings, hide

# Set basic application parameters
USER = username
HOST = 'web105.webfaction.com'
GUNICORN_WORKERS = 1
SITENAME = "test.holdenweb.com"
APPNAME = "test_app"
APP_NAME = APPNAME
APP_PORT = 30123 # Should read port from WebFaction API
URLPATH = "/"

@task
def rhubarb():
    local("echo hello")

## Step 2
## deploy the app
#cd $HOME
#mkdir -p $HOME/lib/python2.7
#easy_install-2.7 flask
#rm -r $HOME/webapps/$APPNAME/htdocs
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
def somefunc():
    from xmlrpclib import ServerProxy
    server = ServerProxy('https://api.webfaction.com/')
    print "Server connection created"
    session_id, account = server.login(username, password)
    print "Session established"

