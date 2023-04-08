from threading import Thread


class ThreadManager(Thread):
    def __init__(self):
        self.threads = []

    def add_thread(self, thread:Thread):
        self.threads.append(thread)

    def start(self):
        for thread in self.threads:
            thread.start() 
    
    def join(self):
        for thread in self.threads:
            thread.join()
