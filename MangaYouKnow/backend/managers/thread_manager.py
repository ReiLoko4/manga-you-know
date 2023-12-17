from backend.utilities import ThreadWithReturnValue as Thread
from time import sleep


class ThreadManager(Thread):
    def __init__(self, threads: list[Thread] = None):
        super().__init__()
        self.threads = threads if threads is not None else []

    def add_thread(self, thread: Thread):
        self.threads.append(thread)

    def start(self):
        for thread in self.threads:
            thread.start()

    def start_and_join_by_num(self, num: int = 5):
        for i in range(0, len(self.threads), num):
            for thread in self.threads[i:i + num]:
                thread.start()
            for thread in self.threads[i:i + num]:
                thread.join()

    def start_and_join(self):
        for thread in self.threads:
            thread.start()
            thread.join()

    def start_with_sleep(self, secs: int = 1):
        for thread in self.threads:
            thread.start()
            sleep(secs)

    def join(self) -> list[any] | None:
        values = []
        for thread in self.threads:
            values.append(thread.join())
        if values:
            return values

    def get_len(self):
        return len(self.threads)

    def get_list_threads(self):
        return list(self.threads)

    def delete_all_threads(self):
        self.threads = []

    def __repr__(self) -> str:
        return f'ThreadManager(threads={self.threads})'
