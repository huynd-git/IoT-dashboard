from confluent_kafka import Producer
import json
import csv
import time

""" VARIABLES """
# Output topic
TOPIC = 'raw-data'

# Kafka producer config
config = {
    'bootstrap.servers': 'kafka-broker:9092'
}


""" HELPER FUNCTIONS """
def delivery_callback(err, msg):
    """
    Called when the Producer poll or flush. Print out message in case of message error or successfully delivered.

    Input:
        - err: Error when deliver msg.
        - msg: the message delivered.
    """
    if err:
        print('ERROR: Message failed delivery: {}'.format(err))
    else:
        # Handling None value
        key_str = msg.key().decode('utf-8') if msg.key() is not None else None
        value_str = msg.value().decode('utf-8') if msg.value() is not None else None

        print("Produced event to topic {topic}: key = {key} value = {value}".format(
            topic=msg.topic(), key=key_str, value=value_str))
        

def main():
    # Initiate the producer
    producer = Producer(config)

    # Send each row of the csv file every 0.2 second.
    # This is for demonstate signals from IoT devices (hopefully)
    with open(r'/usr/src/data/data.csv') as f:
        csvreader = csv.DictReader(f, delimiter=',')
        count = 0
        for row in csvreader:
            producer.produce(topic=TOPIC, value=json.dumps(row).encode('utf-8'), callback=delivery_callback)
            time.sleep(.2)
            count += 1

            # Polling every 1000 msg to prevent backlog
            if count == 1000:
                producer.poll()
        
        producer.flush()

if __name__ == '__main__':
    main()