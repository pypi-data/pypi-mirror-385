# FastStream STOMP broker

## How To Use

Install the package:

```sh
uv add faststream-stomp
poetry add faststream-stomp
```

Basic usage:

```python
import asyncio

import faststream
import faststream_stomp
import stompman

server = stompman.ConnectionParameters(host="127.0.0.1", port=61616, login="admin", passcode="password")
broker = faststream_stomp.StompBroker(stompman.Client([server]))


@broker.subscriber("first")
@broker.publisher("second")
def _(message: str) -> str:
    print(message)  # this will print message from startup
    return "Hi from first handler!"


@broker.subscriber("second")
def _(message: str) -> None:
    print(message)  # this will print message from first handler


app = faststream.FastStream(broker)


@app.after_startup
async def send_first_message() -> None:
    await broker.connect()
    await broker.publish("Hi from startup!", "first")


if __name__ == "__main__":
    asyncio.run(app.run())
```

Also there are `StompRouter` and `TestStompBroker` for testing. It works similarly to built-in brokers from FastStream, I recommend to read the original [FastStream documentation](https://faststream.airt.ai/latest/getting-started).

### Caveats

- When exception is raised in consumer handler, the message will be nacked (FastStream doesn't do this by default)
