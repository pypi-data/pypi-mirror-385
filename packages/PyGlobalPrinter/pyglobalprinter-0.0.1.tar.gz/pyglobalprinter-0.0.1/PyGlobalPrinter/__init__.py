import time
import threading
class printer:
    def __init__(self):
        self.obj = []
        self.running = 1
    def run(self):
        while self.running:
            if self.obj: print(self.obj.pop(0))
            time.sleep(0.01)
    def add(self,stg):
        self.obj.append(stg)
    def main(self):
        threading.Thread(target=self.run, args=(),daemon=1).start()
    def stop(self):
        self.running = 0