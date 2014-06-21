from mbbkeepalive.mbb import has_internet_connectivity, enable_gsm_interface
import time

__author__ = 'vedran'

if __name__ == '__main__':
    while True:
        if not has_internet_connectivity():
            enable_gsm_interface()
        time.sleep(20)