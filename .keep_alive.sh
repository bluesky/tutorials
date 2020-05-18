#!/bin/bash

# Notebooks can take more than 10 minutes to render. Because they produce no
# output to the stdout/stderr while rendering, Travis-CI gives up on us.
# Reassure Travis by printing periodically.
while true
do
    sleep 60
    echo "This line was printed by .keep_alive.sh to keep Travis from giving up due to no output."
    uptime
    free -h
done
