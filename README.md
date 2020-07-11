# Backgammon

* Download Python 3.8 from <https://www.python.org/downloads/>.
* Run `pip install -r requirements.txt` to install dependencies.
* Run `python main.py --server` to host a server with a client.
* Run `python main.py --host {ip}` to connect to a host as a client.
* Th default port is `61096` TCP, which can be changed by passing `--port {port}`.

## TODO

* Make is possible to undo and redo moves. This would allow to if a move was correct or where a piece was placed before.
* Save gamestate to file.
* Show mouse of other player.
* Counter of dieces.
* Place direction hints.