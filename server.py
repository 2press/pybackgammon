from weakref import WeakKeyDictionary

from PodSixNet.Channel import Channel
from PodSixNet.Connection import connection
from PodSixNet.Server import Server
import requests


def get_my_ip():
    url = 'https://api.ipify.org'
    return requests.get(url=url).text


class ClientChannel(Channel):

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

    def Network_ping(self, data):
        self.Send({'action': 'pong'})

    def Close(self):
        self._server.delPlayer(self)


class BackgammonServer(Server):

    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.players = WeakKeyDictionary()
        ip = get_my_ip()
        port = kwargs['localaddr'][1]
        print(f'Starting Server on {ip}:{port}')

    def Connected(self, channel, addr):
        self.addPlayer(channel)
        self.sendPlayers()

    def addPlayer(self, player):
        print("New Player" + str(player.addr))
        self.players[player] = True
        print("players", [p for p in self.players])

    def delPlayer(self, player):
        print("Deleting Player" + str(player.addr))
        del self.players[player]
        self.sendPlayers()

    def sendPlayers(self):
        for p in self.players:
            p.Send({'action': 'playercount', 'count': len(self.players)})

    def sendToOthers(self, data, channel):
        for player in self.players:
            if player != channel:
                player.Send(data)
