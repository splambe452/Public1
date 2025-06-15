import ibapi
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import sys
print(sys.path)
#Class for interacting with the Interactive Brokers API
class IBAPI(EWrapper,EClient):
    def __init__(self):
        EClient.__init__(self, self)

#bot logic
class Bot:
    ib = None
    def __init__(self):
        ib = IBAPI()
        ib.connect("127.0.0.1", 7497,1)
        ib.run()

#Mstart the bot
bot = Bot()
