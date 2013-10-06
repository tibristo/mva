import threading
import time
import adaBoost
class adaThread (threading.Thread):
    def __init__(self, threadID, name, counter, adaB):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.ada = adaB
    def run(self):
        print "Starting " + self.name
        # Get lock to synchronize threads
        #threadLock = threading.Lock()
        #threadLock.acquire()
        self.ada.run()
        # Free lock to release next thread
        #threadLock.release()
