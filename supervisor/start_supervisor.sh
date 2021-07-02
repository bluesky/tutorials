# Locate the directory that contains this script.
DIR=$( cd "$(dirname "$0")" ; pwd -P )
# Start supervisord if is not already running.
[ ! -e /tmp/supervisor.sock ] && supervisord -c $DIR/supervisord.conf
# The processes managed by supervisord are being auto-started.
supervisorctl -c $DIR/supervisord.conf "$@"
