__author__ = 'Steven LI'

class Reverse:
    "Iterator for looping over a sequence backwards"
    def __init__(self, str):
        reverse = list(str)
        reverse.reverse()
        self.data = ''.join(reverse)
        self.index = len(str)
    def __iter__(self):
        return self
    def __next__(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.data[self.index]

    def first(self):
        return self.data[0]
    def last(self):
        return self.data[-1]
    def range(self, first=0, last=-1):
        return self.data[first:last]





