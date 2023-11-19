# The follow code was found in the link above. Thanks for who wrote it.
# https://stackoverflow.com/questions/2777188/making-a-python-iterator-go-backwards


class EnableBackwardIterator:
    def __init__(self, iterator):
        self.iterator = iterator
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
