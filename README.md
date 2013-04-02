Using XMPP for notifications on a Synology NAS
==============================================

Adapted from https://github.com/miracle2k/synology-sipgate-sms

Pre-Requisites
--------------

ipkg
-----
	Install ipkg (see http://forum.synology.com/wiki/index.php/Overview_on_modifying_the_Synology_Server,_bootstrap,_ipkg_etc#How_to_install_ipkg for details)

Python and XMPP.py
-------------------
	$ ipkg install python27
	$ curl -O http://peak.telecommunity.com/dist/ez_setup.py
	$ curl -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py
	$ python2.7 ez_setup.py && python2.7 get-pip.py && rm ez_setup.py get-pip.py

Installation
------------
    $ cd /opt/local
    $ curl -k -L https://github.com/marklr/synology-xmpp/tarball/master | tar -xzv
    $ mv marklr-synology-xmpp-* synology-xmpp
    $ cd synology-xmpp && /opt/local/bin/pip install -r requirements.txt
    $ chmod 755 server.py

Create the configuration file and adjust the parameters:

    $ cd /opt/local/synology-xmpp
    $ cp config.py.dist config.py
    $ vi config.py

Configuration Parameters
-------------------------
	PORT - the port to listen on; set this to a value higher than 1024.
	LOGFILE - log file to write to.
	XMPP_SERVER - defaults to Google's Talk server.
	DESTINATIONS - a list of destinations to send the notifications to.

Note that you need to restart the daemon after making changes.

Create the init script 

    $ cp /opt/local/synology-xmpp/initd-script /opt/etc/init.d/S10synology-xmpp

Start the daemon:

    $ /opt/etc/init.d/S10synology-xmpp start

In the administrative UI, configure the SMS provider (Control Panel -> Notification -> SMS -> SMS service provider -> Add). Name the new provider "XMPP" and use the following url::

    http://localhost:10500/?user=&password=&to=&text=Hello+World

Press "Next", and assign the following categories:


Press the "Send a test SMS message" button to test.


Debugging
---------

You can run ``python2.7 server.py`` on the console to get output. Alternatively, when running as a daemon, a log file will be created in ``/var/log/sipgate-xmpp.log``.