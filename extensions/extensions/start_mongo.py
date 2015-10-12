from subprocess import Popen


def load_jupyter_server_extension(nbapp):
    nbapp.log.info('Mongo-starting extension loaded')
    Popen('mongod')
