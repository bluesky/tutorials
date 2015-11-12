from subprocess import Popen


def load_jupyter_server_extension(nbapp):
    nbapp.log.info('EPICS adsim - extension loaded')
    Popen('procServ -q --name=adsim -i ^C^D^] -c /epics/iocs/adsim 2049 ./st.cmd', shell=True)
