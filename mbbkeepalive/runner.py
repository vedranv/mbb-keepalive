from mbbkeepalive.mbb import MBBKeepAliveExecutor
import time

__author__ = 'vedran'

if __name__ == '__main__':
    executor = MBBKeepAliveExecutor()
    while True:
        executor.execute()
        time.sleep(20)