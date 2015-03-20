from multiprocessing import Process, Manager
from multiprocessing.managers import SyncManager
import time
import signal
import json
import urllib
import urllib2
import driveUp
import sys

class DataSender:

    def __init__(self):
        self.driveup = driveUp.DriveUp('client.json')
        self.running = True
        self._manager = SyncManager()


    def start(self):
        self.driveup.authenticate()
        self._manager.start(self._mgr_init)
        self._que = self._manager.Queue()
        self._process = Process(target=self.up, args=(self._que,))
        self._process.start()

    def _mgr_init(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        print("initialized manager")

    def up(self,que):
        
        def stop(val,val2):
            print "process SIGINT stopping"
            self.running = False

        signal.signal(signal.SIGINT, stop)
        print('datauploader started')
        while self.running or not que.empty():
            try:
                item = que.get(True)
                print("handling item={0}".format(item))
                self.driveup.upload(item)
                que.task_done()
            except:
                print("uploading failed due to exception: {0}".format(sys.exc_info()[0]))
            time.sleep(2)
        print("datauploader process terminating...")

    def send(self, data):
        self._que.put(data)
    
    def stop(self):
        print("shutting down sender")
        self.running = False
        self._que.join()
        self._process.terminate()

if __name__ == '__main__':
    sender = DataSender()
    sender.start()
    sender.send(sys.argv[1])
    sender.send(sys.argv[2])
    # val = 0
    # sample = {'node_id': 'TEST', 'data_type': 'float', 'value': val}
    # try:
    #     while val < 30:
    #         val = val+1
    #         sample['value'] = val
    #         in_json = json.dumps(sample)
    #         print("adding new item to que={0}".format(in_json))
    #         sender.send(in_json)
    #         if val % 2 == 0:
    #             print("main thread will sleep now for 2 seconds")
    #             time.sleep(2)
    # except KeyboardInterrupt:
    #     print("keyboard interrupt")
    #     sender.stop()
    sender.stop()
