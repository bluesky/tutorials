# Start supervisord if is not already running.

# Once jupyter-repo2docker supports a running a script at container
# start time (i.e. ENTRYPOINT) then we can run this that way and
# no action will be required by the user.

DIR=`dirname "\$0"`

supervisorctl -c $DIR/supervisord.conf status
