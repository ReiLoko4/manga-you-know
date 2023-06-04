from threading import Thread
from time import sleep


class ThreadManager(Thread):
    def __init__(self):
        self.threads = []

    def add_thread(self, thread:Thread):
        self.threads.append(thread)

    def start(self):
        for thread in self.threads:
            thread.start() 
    
    def start_and_join(self):
        for thread in self.threads:
            thread.start()
            thread.join()

    def start_with_sleep(self, secs:int=1):
        for thread in self.threads:
            thread.start()
            sleep(secs)
    
    def join(self):
        for thread in self.threads:
            thread.join()
    
    def get_len(self):
        return len(self.threads)
    
    def get_list_threads(self):
        return list(self.threads)

    def delete_all_threads(self):
        self.threads = []
