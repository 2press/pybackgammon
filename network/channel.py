from PodSixNet.Channel import Channel


class BackgammonChannel(Channel):

    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)

    def Network_resetboard(self, data):
        self._server.sendToOthers(data, self)

    def Network_roll(self, data):
        self._server.sendToOthers(data, self)

    def Network_move(self, data):
        self._server.sendToOthers(data, self)

    def Network_impact(self, data):
        self._server.sendToOthers(data, self)

    def Network_eyes(self, data):
        self._server.sendToOthers(data, self)

    def Network_mousemotion(self, data):
        self._server.sendToOthers(data, self)

    def Network_ping(self, _data):
        self.Send({'action': 'pong'})

    def Close(self):
        self._server.delPlayer(self)
