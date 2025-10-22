from abc import abstractmethod
from threading import Thread


class Runnable(Thread):
    thread: Thread
    do_run: bool

    def start(self):
        self.do_run = True
        Thread.start(self)

    def run(self) -> None:
        self.on_start()
        while self.do_run:
            self.work()
        self.on_stop()

    def stop(self, join: bool = True):
        self.do_run = False
        if join:
            self.join()

    def on_start(self):
        ...

    def on_stop(self):
        ...

    @abstractmethod
    def work(self):
        ...


__all__ = ["Runnable"]
