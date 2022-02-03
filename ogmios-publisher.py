import websocket
import json

from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub


ENTRY = "STREAM"
CHANNEL = "ogmios-utxo-data-stream"
ADDR = "addr1q9w227nnschctw75e90zu3kyhnu5rzylc6nxtjtgyue7r0n4g7czyqsfstgew0hc0yw803psx0aqvj4s2wz6x2rkjzzq2937jx"

pnconfig = PNConfiguration()
pnconfig.publish_key = "your-secret-publish-key"
pnconfig.subscribe_key = "your-secret-subscribe-key"
pnconfig.uuid = "your-uuid"

pubnub = PubNub(pnconfig)


def publish(pn, message=""):
    publish_event = {"entry": ENTRY, "update": message}
    envelope = pn.publish().channel(CHANNEL).message(publish_event).sync()

    if envelope.status.is_error():
        print("[PUBLISH: fail]")
        print("error: %s" % status.error)
    else:
        print("[PUBLISH: sent]")
        print("timetoken: %s" % envelope.result.timetoken)


def wsp(ws, methodname="", args={}, reflection={}):
    print(f"Sending {methodname} request...")
    print()

    ws.send(
        json.dumps(
            {
                "type": "jsonwsp/request",
                "version": "1.0",
                "servicename": "ogmios",
                "methodname": methodname,
                "args": args,
                "mirror": reflection,
            }
        )
    )


def on_message(ws, message):
    response = json.loads(message)

    if response["reflection"]["step"] == "INIT":
        point = response["result"]["IntersectionFound"]["tip"]
        print(f"Current tip is {point}, acquiring tip...")
        wsp(ws, "FindIntersect", {"points": [point]}, {"step": "JUMP"})

    elif response["reflection"]["step"] == "JUMP":
        point = response["result"]["IntersectionFound"]["tip"]

        wsp(ws, "Acquire", {"point": point}, {"step": "QUERY"})

    elif response["reflection"]["step"] == "QUERY":
        print("New state acquired, querying UTxO...")
        wsp(
            ws,
            "Query",
            {
                "query": {
                    "utxo": [ADDR],
                },
            },
            {"step": "NEXT"},
        )

    elif response["reflection"]["step"] == "NEXT":
        # Optional logic to-do here to parse any diffs

        publish(pubnub, json.dumps(response["result"], indent=4))
        print("Waiting for next block update...")
        wsp(ws, "RequestNext", {}, {"step": "QUERY"})


def on_error(ws, error):
    print("ERROR")
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def on_open(ws):
    print("Opened connection, finding intersect...")
    wsp(ws, "FindIntersect", {"points": ["origin"]}, {"step": "INIT"})


if __name__ == "__main__":
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(
        "ws://localhost:1337",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    ws.run_forever()
