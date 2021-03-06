## Flask_wf: Easy flask build on WebFaction

The idea behind this system is to make it easy to create Flask-based
web sites on WebFaction's servers in a completely automated way.
Rather than having WF create a Flask/WSGI site themselves and then
editing the configuration to adapt it, we create a web-socket
application and install Apache ourselves as the front-end server.

Since this is early days, there is no accommodation for static files
(which it would clearly be advantageous to have Apache server rather
than Flask).

At present the only usable (and half-way tested) tasks are:

* app_create: creates the new application

* app_delete: deletes the application (leaving the log files in place)

For convenience there are also `server_{stop,start,restart}` tasks to
allow you to manage the server from your local machine.

Some functions may be marked as tasks even though they should not
really be so in a production system. This has been done for testing
purposes.

### Installation

Clone the repository. Create a new virtual environment and install
the necessary dependencies. It's already recorded as an issue that
the requirements file describes dependencies for both testing and
deployment, but for now it's convenient not to have to create two
separate virtualenvs.

```
pip install -r requirements.txt
```

At this point I have no reliable way to run the flask server locally.
When that comes along you should be able to run it with the command

```
python apache2/htdocs/main/__init__.py
```

This could probably be done relatively easily with another fab task.

Create
a file in the project's root directory called `credentials.py` which
assigns your WebFaction username to the `username` variable and your
WebFaction password to the`password` variable. This file is ignored
by git, and so should not show up in repositories.

To deploy, ensure that all necessary parameters are established in the
`fabfile.py` file (the changes should all be between the two rows of
hash marks towards the top of the file). Then run the command

```
fab app_create
```

To remove your existing site to prepare for a new deployment you should
run

```
fab app_delete
```

