# The follow code was found in the link above. Thanks for who wrote it.
# https://stackoverflow.com/questions/2777188/making-a-python-iterator-go-backwards
# I just made some changes to fit my needs.

from typing import Iterator, Union


class EnableBackwardIterator:
    def __init__(self, iterator: Union[list, Iterator]):
        self.length = len(iterator)
        self.iterator = iterator \
            if isinstance(iterator, Iterator) else iter(iterator)
        self.history = [None, ]
        self.i = 0

    def next(self):
        self.i += 1
        if self.i < len(self.history):
            return self.history[self.i]
        else:
            elem = next(self.iterator)
            self.history.append(elem)
            return elem

    def prev(self):
        self.i -= 1
        if self.i == 0:
            raise StopIteration
        else:
            return self.history[self.i]
        
    def peek_next(self):
        if self.i + 1 < len(self.history):
            return self.history[self.i + 1]
        else:
            elem = next(self.iterator)
            self.history.append(elem)
            return elem
        
    def peek_prev(self):
        if self.i - 1 <= 0:
            raise StopIteration
        else:
            return self.history[self.i - 1]

    def delete_next(self):
        self.length -= 1
        if self.i + 1 < len(self.history):
            del self.history[self.i + 1]

    def change_current(self, new_value):
        if self.i < len(self.history):
            self.history[self.i] = new_value
        else:
            raise IndexError("Current index is out of range")
        
    def __len__(self):
        return self.length
