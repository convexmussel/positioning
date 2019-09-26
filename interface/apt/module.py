from string import Template

import math

from protocol.message import Message


class Module:

    def __init__(self, controller, channel, max_travel, closed_loop):
        # Save reference to controller interface
        self.controller = controller
        # Save the channel of this specific Module on controller
        self.channel = channel
        # Create template string for channel, get channel value from controller interface's constant
        destination = Template('bay${channel}')
        self.destination = controller.SOURCE_DESTINATION[destination.substitute(channel=channel)]

        # The controller has 10 channels that are possible to connect to
        self.max_channels = 10
        # Supported messages, not initialised yet, they're initialised as neededd
        self.closed_loop_enable_message = None
        self.closed_loop_disable_message = None
        self.zeropos_message = None
        self.move_message = None
        self.statusbits_message = None
        self.reg_outputpos_message = None

        self.closed_loop = closed_loop
        self.location = None
        # data from registers
        self.status_bits = None
        self.outputpos = None

        # Set maximum piezo travel
        self.max_travel = max_travel
        self.max_voltage = 75
        self.max_bytes = 35767
        # Enable closed loop mode, set piezo to zero
        #self.set_closed_loop(False)

    def move_closed(self, position):
        # Build a pz_set_outputpos message (0x0646), it has a data size of 4 (0x04)
        self.location = position
        if self.move_message is None:
            self.move_message = Message(0x0646, 0x04, self.destination)

        # Clear previous message data
        self.move_message.clear_data()

        # limit movement between maximum movement and zero
        travel_micron = max(min(self.max_travel, position), 0)

        # output position is a 0 - 100% value based on 0 - 32767 decimal values
        # calculates the total movement value and creates a hex value from this
        travel_percentage = travel_micron / self.max_travel
        outputpos = math.floor(travel_percentage * 32767)
        # Add the channel indent to the message, 01 by default, 2 bytes in size
        self.move_message.add_word(0x0001)
        # Ad the output position to the message, as calculated, 2 bytes in size
        self.move_message.add_word(outputpos)

        self.controller.write_data(self.move_message.get_data())

    def move_open(self, position):

        # Build a pz_set_outputpos message (0x0646), it has a data size of 4 (0x04)
        self.location = position
        if self.move_message is None:
            self.move_message = Message(0x0643, 0x04, self.destination)

        # Clear previous message data
        self.move_message.clear_data()

        # limit movement between maximum movement and zero
        travel_micron = max(min(self.max_travel, position), 0)

        output_scale = travel_micron/self.max_travel
        output_bytes = math.ceil(output_scale * self.max_bytes)
        # Add the channel indent to the message, 01 by default, 2 bytes in size
        self.move_message.add_word(0x0001)
        # Ad the output position to the message, as calculated, 2 bytes in size
        self.move_message.add_word(output_bytes)

        self.controller.write_data(self.move_message.get_data())

    def move(self, position):
        if self.closed_loop:
            self.move_closed(position)
        else:
            self.move_open(position)

    def zero(self):
        # Build a message that sets the Piezo to zero position if it doesn't yet exist
        if self.zeropos_message is None:
            self.zeropos_message = Message(0x0658, [0x01, 0x00], self.destination)

        self.controller.write_data(self.zeropos_message.get_data())
        self.location = 0.0

    def get_status_bits(self):
        print(self.destination)
        for x in range(10):
            self.statusbits_message = Message(0x065B, [x, 0x00], self.destination)
            print(self.statusbits_message.get_data())
            self.controller.write_data(self.statusbits_message.get_data())

            self.status_bits = self.controller.interface.read_data_bytes(12, 3)
            print(self.status_bits)

    def get_zero_status(self):
        self.get_status_bits()
        if self.status_bits[11] & 0x10 == 0x10:
            return True
        return False

    def get_location(self):
        destination = self.controller.SOURCE_DESTINATION["rack/motherboard"]
        if self.reg_outputpos_message is None:
            self.reg_outputpos_message = Message(0x0647, [0x00, 0x00], destination)
        self.controller.write_data(self.reg_outputpos_message.get_data())

        data_packet = self.controller.interface.read_data_bytes(10, 3)
        # calculate the 16 bit output position by shifting the MSB 8 bits and add the lsb
        self.outputpos = (data_packet[8] << 8) + data_packet[9]

    def set_closed_loop(self, enable):
        if self.closed_loop_disable_message is None:
            # Build a message that sets the Piezo control mode to open loop mode
            self.closed_loop_disable_message = Message(0x0640, [0x01, 0x03], self.destination)
        if self.closed_loop_enable_message is None:
            # Build a message that sets the Piezo control mode to closed loop mode
            self.closed_loop_enable_message = Message(0x0640, [0x01, 0x04], self.destination)

        if enable:
            self.controller.write_data(self.closed_loop_enable_message.get_data())
        else:
            self.controller.write_data(self.closed_loop_disable_message.get_data())
