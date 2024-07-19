import nsq
import tornado.ioloop

def print_handler(message):
    # Process the message
    data = message.body.decode('utf-8')
    print(f"Processing message: {data}")
    # Acknowledge that the message has been processed
    message.finish()

def run():
    reader = nsq.Reader(
        message_handler=print_handler,
        lookupd_http_addresses=['http://127.0.0.1:4201'],  # Adjust this to your nsqlookupd HTTP port
        topic='print_topic',
        channel='print_channel',
        max_in_flight=9
    )
    nsq.run()

if __name__ == '__main__':
    run()
