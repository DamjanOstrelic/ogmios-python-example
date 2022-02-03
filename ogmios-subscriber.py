from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

CHANNEL = "ogmios-utxo-data-stream"

pnconfig = PNConfiguration()
pnconfig.subscribe_key = "your-secret-subscribe-key"
pnconfig.uuid = "your-uuid"

pubnub = PubNub(pnconfig)


class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, event):
        print("[PRESENCE: {}]".format(event.event))
        print("uuid: {}, channel: {}".format(event.uuid, event.channel))

    def status(self, pubnub, event):
        if event.category == PNStatusCategory.PNConnectedCategory:
            print("[STATUS: PNConnectedCategory]")
            print("connected to channels: {}".format(event.affected_channels))

    def message(self, pubnub, event):
        print("[MESSAGE received]")
        print("{}: {}".format(event.message["entry"], event.message["update"]))


pubnub.add_listener(MySubscribeCallback())
pubnub.subscribe().channels(CHANNEL).with_presence().execute()

print("***************************************************")
print("* Waiting for address updates... *")
print("***************************************************")
