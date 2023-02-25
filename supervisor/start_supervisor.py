"""
This script facilitates additional configurations that may be
required for launching virtual IOCs on your operating system.
The functionality is wrapped up in __start_supervisor method
so as to not pollute your running scope.
"""


def __start_supervisor():

    import os
    import sys
    import getpass
    from argparse import ArgumentParser
    import configparser
    import shlex
    from pathlib import Path
    import subprocess
    from subprocess import STDOUT, PIPE

    config_dir = os.path.join("supervisor", "conf.d")
    config_parser = configparser.RawConfigParser()
    command_parser = ArgumentParser()
    command_parser.add_argument("--interfaces", nargs="*")

    # Yield "command" option from all sections in a given .conf file path
    def parse_config_file(config_file_path):
        with open(config_file_path, "r") as cfile:
            config_parser.read_file(cfile)
            for section in config_parser.sections():
                if config_parser.has_option(section, "command"):
                    yield config_parser.get(section, "command")

    # Parse command string and returns all loopback interfaces as a list
    def extract_interfaces(command):
        argv = shlex.split(command)
        parsed, _ = command_parser.parse_known_args(argv)
        if parsed.interfaces is not None:
            return parsed.interfaces
        return []

    # Configure macOS loopback interface for virtual IOCs
    def macos_config(start=True):
        action = "alias" if start else "-alias"
        passwd = getpass.getpass("password:")
        passwd = shlex.quote(passwd)
        interfaces = []
        for file in Path(config_dir).glob("*.conf"):
            for command in parse_config_file(file):
                interfaces += extract_interfaces(command)
        for interface in set(interfaces):
            interface = shlex.quote(interface)
            cmd = f"echo {passwd} | sudo -Sp '' ifconfig lo0 {action} {interface}"
            proc = subprocess.Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
            res, _ = proc.communicate()
            exit_code = proc.wait()
            if exit_code:
                print(res.decode(), file=sys.stderr)
                break

    # Pass arguments to supervisor
    def supervisor_cmd(argv):
        subprocess.run([os.path.join("supervisor", "start_supervisor.sh"), *argv])

    if sys.platform == "darwin":
        if "--shutdown" in sys.argv[1:2]:
            macos_config(start=False)
            supervisor_cmd(["stop", "all"])
        else:
            macos_config(start=True)
            supervisor_cmd(sys.argv[1:])
    else:
        supervisor_cmd(sys.argv[1:])


__start_supervisor()
del __start_supervisor
