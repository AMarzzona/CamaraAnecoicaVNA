import pyvisa


class MTR:

    def __init__(self, resource):
        rm = pyvisa.ResourceManager()
        self.mtr = rm.open_resource(resource)

    def rotate_rx(self):

        pass

    def rotate_tx(self):

        pass
