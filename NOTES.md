# Notes on the Flask_WebFaction Project

This project is intended as a "starter kit" to encourage those relatively new
to the open source web to follow better practices than they otherwise might,
thereby saving time and avoiding frustration.

Whether you, dear reader, are a beginner or an experienced hand, ***you can
help this project***. Please contact us about ***anything*** in this document
(or in the rest of the project) which does not seem clear. It is way too easy
for the person who designs a procedure to overlook obvious gaps in the
information they provide, so all feedback will be valuable and will, indeed,
give this project any real value it has.

For example, you are probably wondering why the project is called what it is.
That's because I am using a Python web server called `flask` hosted by a
company called *WebFaction*. If you aren't, the best you can hope for is
that these instructions might offer you a guide.

To let you try things yourself (assuming you have an account with WebFaction
and want to run `flask`) the project includes a fabric file (which in turn
requires that your local Python has Fabric and a few other things installed.
At present the requirements for deployment (i.e. what you need in your local
Python to install web applications on your WebFaction account) are not
separated from the production requirements, something that needs thought
before too long.

So far ()10:30 on 2015-1-25) I can create a remote application and transfer
the source files up to the application directory. Now I should add a few files
to the project to allow use of "git clean".

UPDATE 2015-01-26:

The git clean distribution seems to work for what it's worth.

Now at the stage where I have got the local server to work (just run the
module's __init__.py as a main program). So now I need to see whether the
deployment step is going to work. This means making sure I have munged the
default apache httpd.config into something more usable. Or perhaps not. I
haven't yet addressed the issue of handling static files. This my be
different from a local system. Not important yet!

At this stage I can now install an app and have it prepare a usable virtual
environment (as long as I rememebr to use `run_venv` when I want to use it).
This appears to overcome the installation bugs where the requirements file
conflicted with the standard Python's installed files in /usr/local.

UPDATE 2015-1-28

I have now confirmed by experiment that the WSGIPythonHome directive IS
required - without it, local stuff from ~/lib gets included in the path
thanks to WebFaction's special build(?) and/or 

Good information from Aaron Presley about the required structure of
the HTTPD control file at

  http://aaronpresley.com/deploying-a-flask-project-on-webfaction/

With this as a guide, plus stuff gleaned from

  http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/#troubleshooting
  
I have managed to get the system working reliably, and only need to diff
the file and find a way to make the necessary entries in httpd.conf. At
present I am adding the path in the index.py (my application.wsgi file
equivalent - the important thing is that it's aliased to the root handler
in the WSGIScriptAlias directive) - want to see whether we can avoid the
need to change sys.path by adding a WSGIPythonPath directive to the
httpd.conf file. This seems not to work, but I'll play with it a little
longer.


UPDATE 2015-01-30

Seems like the thing to do is to add the directory on the WSGIScriptAlias
directive using the PATH option. If we do this there is no need to muck
with sys.path in index.py, but it gives us an ugly editing task, so the
sys.path modification in index.py file stays. I have also verified the
absolute necessity of the WSGIPythonPath directive to activate the
virtual environment. Woot!

Given that the complexity of the Flask application will grow quickly, I
need to adopt some best practices.

The editing system for config files and the like is ungainly, and likely
to become more so. It would be nice to have a better way to encode the
necessary changes, and then simply apply a standard editing paradigm to
any file that needs to be changed. It might also be appropriate to use
something like Jinja template transformation before the file is used to
control editing, so the process relies less on string construction
inside the logic.

To get a handle on the process I took a diff between the installed 
httpd.conf and the same file in a brand new wsgi/Python application.
The changes are annotated below.
```
--- httpd.conf7 2015-01-30 21:05:31.000000000 +0000
+++ apache2/conf/httpd.conf     2015-01-30 19:12:15.000000000 +0000
@@ -10,21 +10,25 @@

 LogFormat "%{X-Forwarded-For}i %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined
 CustomLog /home/sholden/logs/user/access_new_app_6.log combined
-DirectoryIndex index.py
-DocumentRoot /home/sholden/webapps/new_app_6/htdocs
+DocumentRoot /home/sholden/webapps
 ErrorLog /home/sholden/logs/user/error_new_app_6.log
 KeepAlive Off
-Listen 32292
+Listen 26505
 MaxSpareThreads 3
 MinSpareThreads 1
 ServerLimit 1
 SetEnvIf X-Forwarded-SSL on HTTPS=1
 ThreadsPerChild 5
-WSGIDaemonProcess new_app_6 processes=5 python-path=/home/sholden/webapps/new_app_6/lib/python3.4 threads=1
+WSGIPythonHome /home/sholden/webapps/new_app_6/venv/bin
+WSGIScriptAlias / /home/sholden/webapps/new_app_6/htdocs/index.py
+WSGIDaemonProcess new_app_6 processes=5 python-path=/home/sholden/webapps/new_app_6:/home/sholden/webapps/new_app_6/venv/lib/python2.7 thread
s=1
 WSGIProcessGroup new_app_6
 WSGIRestrictEmbedded On
 WSGILazyInitialization On

 <Directory /home/sholden/webapps/new_app_6/htdocs>
-    AddHandler wsgi-script .py
+    RewriteEngine on
+    RewriteBase /
+    WSGIScriptReloading On
+    # AddHandler wsgi-script .py
 </Directory>
 ```
 
 The "mini-language" for editing could, technically, be provided as a
 templated diff file. I was thinking of something simpler, but it
 might just possibly work! Let me do a little experimenting.
 
 To create the patch file:
 
 1. Take a copy of the new_app_6 configuration file and edit all
    the occurrences of "new_app_6" to "new_app_7".
 2. Create a "new_app_7" application and move the copy from 1
    above into it as "patched.conf"
 3. Diff the files to produce a difference file that will turn
    the installed file into the patched one.
    
    Apparently "diff -Naur old new" in the directory of interest is
    the preferred way to generate patch files.

This shouldn't be a horrendous task - the edits would take all of a minute
or two to apply manually.

So I now have a file called "httpd.conf.patch" that should fix up a
configuration file once the {{ APP_NAME }} variable is subsituted. So
theoretically it's parameterised.

The strategy is now to create a new app with the existing code minus the
httpd.conf fixup, then create a parameterized copy of the patch file and
apply it, then see if the application works.

UPDATE 2015-01-31

But patching seems less capable that editing with sed, so why don't I
just do that instead (like the script I originally despised did)? I
could do substitution in the edit script, but it might be more cumbrous.
Where's that freaking script?

Good notes, potentially useful, about project layout in

  https://github.com/imwilsonxu/fbone
  

UPDATE 2015-02-01

Tried a different approach today. Rather than creating the app as a
WebFaction WSGI app I tried copying the whole Apache installation
from another site and just creating a web socket application in the
Web Faction parlance. Unfortunately for some reason this doesn't
work.

Could be because I didn't parameterize the apache2/bin shell scripts,
I guess. Let me find out ... yup, fixing that error (i.e. making sure
the script contains the right app name) left me with a listening socket
on the configured port. Go me! This means that there will be a number
of files (4) to parameterize, making it well worth using jinja!

Cool, so now I have restructured the app so its code can live in the
htdocs/main directory. This meant a further edit of the httpd.conf file,
and also we had to change the `index.py` file to import from `main`
rather than from `htdocs`. It's slowly becoming apparent to me what's
going on in flask applications.

So my project structure all lives, to make it simple, in the htdocs
directory. I have added an empty subdirectory to act as DocumentRoot
just in case of configuration errors and restructured the project,
whose layout is now a lot more rational (as in, I feel I could
probably defend it if I had to).

This new structure is designed to install everything, with the web
server being configured and installed as a part of our installation
process rather than as part of the application creation. So now we
should be creating a simple socket application, extracting the socket
number from the application, and configuring it from the application
environment.

Hopefully this will result in a more controllable process. We shall
see.

UPDATE 2015-02-02

Currently getting "no such file or directory" when I try to enumerate
the files in the "apache2" directory. That was because I was trying to
use a string instead of a list for the command!

Now trying to create those files remotely, having substituted for the
app_name and port number in binary and conf files and failing with a
"no such file or directory" error on apache2/bin.start. Since restart
always tells me Apache is not running I suspect issues with the pidfile.
Let us see...

Yes, the issue seems to be that a WebFaction-created app has a logs
subdirectory (even though logging takes place to another directory
entirely). However, when I tried to establish a PidFile in the conf
file I still see the error. Maybe my hypothesis is wrong?

Strangely, I see no error when I try to start Apache manually with the
newly-established start file. When I do, however, index.py complains
that there is no "main" package to import the application from. This
is puzzling.

Well the pidfile is being created, so maybe the issue is the main
problem? Need to investigate. Aha, the indentation level on the run
command to start apache was the issue - one too few levels and it was
not being run on the correct directory context.

There is a problem with the pidfile being in the logs area - because
it doesn't get deleted when the app is deleted, the start script
incorrectly assumes Apache is running when it starts up. The way round
this issue is to include a "logs" subdirectory under the apache2
directory so that there is somewhere for the default pidfile to be
created.

Woot! After many tribulations I now have a working process, which serves
the web content immediately after installation. This is an achievement
of sorts, and so the next period of effort should be to make sure that
source code control is brought up to date and then think about engineering
for greater robustness and increased flexibility.