from subprocess import Popen


def load_jupyter_server_extension(nbapp):
    npapp.log.info('EPICS adsim - extension loaded')
    Popen('procServ -q -n ‘adsim’ -i ^C^D^] -c /epics/iocs/adsim 2049 ./st.cmd')
