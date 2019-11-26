from string import Template

from piezo.interface.apt.controller import Controller
from piezo.interface.apt.module import Module
from piezo.protocol.message import Message


class APT:
    def __init__(self, closed_loop):
        self.controller = Controller()
        self.modules = dict()

        for x in range(10):

            destination = self.controller.SOURCE_DESTINATION["rack/motherboard"]
            bay_used_message = Message(0x0060, [x, 0x00], destination)

            self.controller.write_data(bay_used_message.get_data())
            response = self.controller.read_data(6, 3)
            if response[3] == 0x01:
                module_name = Template('module$indent')
                self.modules[module_name.substitute(indent=x + 1)] = Module(self.controller, x, 30, closed_loop)

    def disconnect(self):
        disconnect_message = Message(0x0002, [0x00, 0x00], 0x11)
        self.controller.write_data(disconnect_message.get_data())
