import ibapi
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract 
from ibapi.order import *
import time
import threading

import sys
print(sys.path)
#Class for interacting with the Interactive Brokers API
class IBAPI(EWrapper,EClient):
    def __init__(self):
        EClient.__init__(self, self)
    #LISTEN for market data updates
    def realtimeBar(self, reqId, time, open_, high, low, close, volume, wap, count):
        bot.on_bar_update(reqId, time, open_, high, low, close, volume, wap, count)
#bot logic
class Bot:
    ib = None
    def __init__(self):
        #Initialize the IBAPI client and connect to the TWS or IB Gateway
        self.ib = IBAPI()
        self.ib.connect("127.0.0.1", 7497,1)
        ib_thread = threading.Thread(target=self.run_loop, daemon=True)
        ib_thread.start()
        time.sleep(1)
        #Create a contract for the stock you want to trade
        symbol = input("Enter the stock symbol: ")
        #create our IB contract OBJECT
        contract = Contract()
        contract.symbol = symbol.upper()
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        #Request market data for the contract
        self.ib.reqRealTimeBars(0, contract, 5, "TRADES", 1, [])
        #Wait for market data to be received
        time.sleep(2)
    #listen to socket in separate thread
    def run_loop(self):
        self.ib.run()

    # pass real-time bar data to the bot 
    def on_bar_update(self, reqId, time, open_, high, low, close, volume, wap, count):
        print(f"Real-time bar update: {reqId}, Time: {time}, Open: {open_}, High: {high}, Low: {low}, Close: {close}, Volume: {volume}, WAP: {wap}, Count: {count}")
        # Here you can implement your trading logic based on the received data

#Mstart the bot
bot = Bot()
