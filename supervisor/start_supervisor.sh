#!/bin/bash

# Locate the directory that contains this script.
DIR=$( cd "$(dirname "$0")" ; pwd -P )

# Start supervisord if is not already running.
# (Include a sleep to reduce chances of a race between IOC startup
# and subsequent code that relies on IOCs being started.
# This race is unlikely to matter for interactive use but can come up
# in the context of CI when cells are executed top-to-bottom.)
[ ! -e /tmp/supervisor.sock ] && supervisord -c $DIR/supervisord.conf && sleep 2

# The processes managed by supervisord are being auto-started.
if [ $# -gt 0 ]; then
  # Passthrough if arguments are passed in
  supervisorctl -c $DIR/supervisord.conf "$@"
else
  # Default to show status
  supervisorctl -c $DIR/supervisord.conf status
fi
