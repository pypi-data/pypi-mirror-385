
from node import ExampleNode
from ebs.linuxnode.gui.kivy.utils.application import BaseIOTNodeApplication


class ExampleApplication(BaseIOTNodeApplication):
    _node_class = ExampleNode
