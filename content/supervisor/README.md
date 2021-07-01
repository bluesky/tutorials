This tutorial uses supervisor, running with non-root permissions, to manage the
caproto IOC(s).

The user needs to start ``supervisord``, which will then automatically start any
IOCs as configured in the ``conf.d/`` subdirectory here.  We provide a
convenience script, ``start_supervisord.sh`` which tries to detect whether
``supervisord`` is already running (with the desired configuration) and, if not,
run it.

Debugging suggestions:

* Check status: ``supervisorctl -c supervisord.conf status``
* Restart all: ``supervisorctl -c supervisord.conf restart all``
* Supervisor's logs are in ``/tmp/supervisor.log``.
