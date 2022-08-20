from weakref import WeakKeyDictionary

from PodSixNet.Server import Server
import requests

from network import BackgammonChannel


class BackgammonServer(Server):

    channelClass = BackgammonChannel

    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.players = WeakKeyDictionary()
        ip = self._getMyIp()
        port = kwargs['localaddr'][1]
        print(f'Starting Server on {ip}:{port}')

    def Connected(self, channel, _addr):
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

    def _getMyIp(self):
        return requests.get(url='https://api.ipify.org').text
