from backend.utilities import ThreadWithReturnValue as Thread
from time import sleep


class ThreadManager(Thread):
    def __init__(self, threads: list[Thread] = None):
        super().__init__()
        self.threads: list[Thread] = threads if threads is not None else []
        self.storage = []

    def add_thread(self, thread: Thread):
        self.threads.append(thread)

    def add_threads(self, threads: list[Thread]):
        self.threads.extend(threads)

    def add_thread_by_args(self, target: any, args: tuple[any] = (), kwargs: dict[str, any] = {}):
        self.threads.append(Thread(target=target, args=args, kwargs=kwargs))
        self.storage.append((target, args, kwargs))

    def start(self):
        for thread in self.threads:
            thread.start()
    
    def start_and_save(self):
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
        
    def restart(self):
        """
        ** WARNING **

        Just works if the threads are created by add_thread_by_args
        """
        self.threads = []
        for target, args, kwargs in self.storage:
            self.threads.append(Thread(target=target, args=args, kwargs=kwargs))

    def get_len(self):
        return len(self.threads)

    def get_list_threads(self):
        return list(self.threads)

    def delete_all(self):
        self.threads = []
        self.storage = []

    def __repr__(self) -> str:
        return f'ThreadManager(threads={self.threads})'
