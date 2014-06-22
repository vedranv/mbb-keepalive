import subprocess
import requests
import smtplib
from email.mime.text import MIMEText
import os
from BeautifulSoup import BeautifulSoup
import netifaces


class Tele2TpoParser(object):
    def __init__(self, output):
        super(Tele2TpoParser, self).__init__()
        self.output = output
        self.tpo = self._parse()

    def _parse(self):
        bs = BeautifulSoup(self.output)
        divs = bs.findAll('div')
        tpo = {}
        for div in divs:
            parsing_data_info = False
            parsing_money_info = False
            ps = div.findAll('p')
            for p in ps:
                if 'informacije o stanju' in unicode(p).lower():
                    parsing_money_info = True
                if '- stanje mb (opcije)' in unicode(p).lower():
                    parsing_data_info = True

            target_p = div.findAll('p', {'class': 'text-info text-center'})
            if parsing_money_info:
                tpo['prepaid_remaining'] = float(target_p[0].string.strip(' KN'))
            if parsing_data_info:
                for idx, p in enumerate(target_p):
                    if idx == 0:
                        tpo['option_remaining'] = int(p.string.strip(' MB'))
                    elif idx == 1:
                        tpo['promo_remaining'] = int(p.string.strip(' MB'))
                    else:
                        raise Exception('Invalid entry. Expecting only two values')

        return tpo


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
        response = requests.get('http://74.125.228.100')
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


def get_tpo():
    response = requests.get('http://mbb.tele2.hr/fetch/tpo')
    parser = Tele2TpoParser(response.content)
    return parser.tpo


def get_mbb_ip():
    return str(netifaces.ifaddresses('ppp0'))

def send_mail(subject, message):
    _to = os.getenv('MAIL_TO')
    _from = os.getenv('MAIL_FROM')

    to_emails = _to.split(',')
    if len(to_emails) > 0:
        main_to = to_emails[0]

    smtp = smtplib.SMTP(os.getenv('SMTP_SERVER'), os.getenv('SMTP_PORT'))
    if os.getenv('SMTP_USE_TLS') == 'true':
        smtp.starttls()
    smtp.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'))

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = _from
    msg['To'] = main_to

    smtp.sendmail(_from, to_emails, msg.as_string())
    smtp.quit()


class MBBKeepAliveExecutor(object):
    def __init__(self):
        super(MBBKeepAliveExecutor, self).__init__()
        self.service_up_notification_sent = False
        self.low_bandwith_notification_sent = False
        self.ip_address = None

    def execute(self):
        if not has_internet_connectivity():
            enable_gsm_interface()

        if has_internet_connectivity():
            self.tpo = get_tpo()
            self.new_ip_address = get_mbb_ip()
            self.send_notification_if_needed()

    def send_notification_if_needed(self):
        message = ''
        needs_mail_send = False
        subject = None
        if not self.service_up_notification_sent:
            needs_mail_send = True
            self.service_up_notification_sent = True
            subject = 'Notifikacija - servis pokrenut'
            message += 'MBB servis pokrenut i internet aktivan\n'
        if self.new_ip_address != self.ip_address:
            needs_mail_send = True
            message += 'Nova ip adresa: %s\n' % self.new_ip_address
            self.ip_address = self.new_ip_address
        if self.tpo and self.tpo['option_remaining'] < 100:
            needs_mail_send = True
            self.low_bandwith_notification_sent = True
            subject = 'Notifikacija - nisko stanje prepaid opcije'
            message += 'Nisko stanje prepaid opcije. Preostalo samo %d MB\n' % self.tpo['option_remaining']
        if self.tpo:
            message += 'Stanje prepaid %f kn\n' % self.tpo['prepaid_remaining']
            message += 'Stanje opcije %d MB\n' % self.tpo['option_remaining']
            message += 'Stanje promotivnog paketa %d MB\n' % self.tpo['promo_remaining']

        if not subject:
            subject = 'Notifikacija MBB'
        if needs_mail_send:
            send_mail(subject, message)

if __name__ == '__main__':
    if not has_internet_connectivity():
        enable_gsm_interface()