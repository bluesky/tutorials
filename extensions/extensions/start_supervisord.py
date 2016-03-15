from subprocess import Popen


def load_jupyter_server_extension(nbapp):
    nbapp.log.info('Supervisord-starting extension loaded')
    Popen('/usr/bin/supervisord')
