from kafka import KafkaProducer
import websocket
import sys

try:
    import thread
except ImportError:
    import _thread as thread
import time
import json

class Listener(object):
    def __init__(self, producer, topic, url, wsRequest=None):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(url,
                on_message = self.on_message,
                on_error = self.on_error,
                on_close = self.on_close,
                on_open = self.on_open)
        self.wsRequest = wsRequest
        self.producer = producer
        self.topic = topic

    def on_message(self, message):
        producer.send(self.topic, json.dumps(message).encode('utf-8'))

    def on_error(self, error):
        print(error)
        sys.exit()

    def on_close(self):
        print("### Connection Closed ###")

    def on_open(self):
        self.ws.send(json.dumps(self.wsRequest))
        print("### Connection Open ###")

    def run(self):
        self.ws.run_forever()

producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

try:
    subscription = {
        "method": "SUBSCRIBE",
        "params": [
            "btcusdt@aggTrade",
            "ethusdt@aggTrade",
            "ltcusdt@aggTrade"
        ],
        "id": 1
    }
    listener = Listener(producer=producer, topic="cryptotrades", url = "wss://stream.binance.com:9443/stream?streams=btcusdt@aggTrade/ethusdt@aggTrade/ltcusdt@aggTrade", wsRequest = subscription)
    listener.run()
except Exception as e:
    print(e)
    sys.exit()
