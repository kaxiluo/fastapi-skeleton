from abc import ABCMeta, abstractmethod

from fastapi import FastAPI


class Provider(metaclass=ABCMeta):

    def __init__(self, app: FastAPI):
        self.app = app

    # @abstractmethod
    def register(self):
        pass

    # @abstractmethod
    def boot(self):
        pass
