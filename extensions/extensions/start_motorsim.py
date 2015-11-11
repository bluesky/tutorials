from subprocess import Popen


def load_jupyter_server_extension(nbapp):
    npapp.log.info('EPICS motorsim - extension loaded')
    Popen('procServ -q -n ‘motorsim’ -i ^C^D^] -c /epics/iocs/motorsim 2048 ./st.cmd')
