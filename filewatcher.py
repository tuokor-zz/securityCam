import pyinotify
import asyncore
import datasender
import os


wm = pyinotify.WatchManager()
mask = pyinotify.IN_CLOSE_WRITE

Up = datasender.DataSender()
Up.start()

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        if ".git" not in event.pathname:
            print("uploading file {0}".format(event.pathname))
            Up.send(event.pathname)


notifier = pyinotify.AsyncNotifier(wm, EventHandler())
wdd = wm.add_watch(os.getcwd(), mask, rec=True)

asyncore.loop()

