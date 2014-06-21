import subprocess
import requests


class NMCliConList(object):
    def __init__(self, output):
        super(NMCliConList, self).__init__()
        self.output = output
        self.interfaces = self._parse()

    def _parse(self):
        out = self.output.split('\n')

        interfaces = []
        for idx, line in enumerate(out):
            if idx == 0:
                name_idx = line.index('NAME')
                uuid_idx = line.index('UUID')
                type_idx = line.index('TYPE')
                timestamp_real_idx = line.index('TIMESTAMP-REAL')
            elif len(line.strip()) == 0:
                continue
            else:
                interface = {'name': line[name_idx:uuid_idx].strip(),
                             'uuid': line[uuid_idx:type_idx].strip(),
                             'type': line[type_idx:timestamp_real_idx].strip(),
                             'time': line[timestamp_real_idx:].strip()}
                interfaces.append(interface)

        return interfaces

    @property
    def gsm_interfaces(self):
        return [x for x in self.interfaces if x['type'] == 'gsm']

    def has_gsm_interface(self):
        return len(self.gsm_interfaces) > 0


def has_internet_connectivity():
    has_connectivity = False
    try:
        response = requests.get('http://google.com')
        if response.status_code == 200:
            has_connectivity = True
    finally:
        return has_connectivity


def enable_gsm_interface():
    output = subprocess.check_output(['nmcli', 'con', 'list'])
    nmcli = NMCliConList(output)

    subprocess.call(['nmcli', 'nm', 'wwan', 'off'])
    if nmcli.has_gsm_interface():
        subprocess.call(['nmcli', 'nm', 'wwan', 'on'])

if __name__ == '__main__':
    if not has_internet_connectivity():
        enable_gsm_interface()