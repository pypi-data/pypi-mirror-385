from time import sleep
from unittest import TestCase

from pyrunnable import Runnable


class ThreadObject(Runnable):
    name = 'ThreadObject'
    started: bool = False
    working: bool = False
    stopped: bool = False

    def on_start(self):
        self.started = True

    def work(self):
        self.working = True
        sleep(1)

    def on_stop(self):
        self.working = False
        self.stopped = True


class Test(TestCase):
    def test(self):
        self.obj = ThreadObject()
        self.obj.start()
        self.assertTrue(self.obj.do_run)
        sleep(1)
        self.assertTrue(self.obj.started)
        sleep(1)
        self.assertTrue(self.obj.working)
        self.obj.stop()
        self.assertFalse(self.obj.working)
        self.assertTrue(self.obj.stopped)
