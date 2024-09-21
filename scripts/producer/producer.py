from confluent_kafka import Producer
import json
import csv
import time

config = {
    'bootstrap.servers': 'kafka-broker:9092'
}

producer = Producer(config)
topic = 'raw-data'


def delivery_callback(err, msg):
    if err:
        print('ERROR: Message failed delivery: {}'.format(err))
    else:
        key_str = msg.key().decode('utf-8') if msg.key() is not None else None
        value_str = msg.value().decode('utf-8') if msg.value() is not None else None

        print("Produced event to topic {topic}: key = {key} value = {value}".format(
            topic=msg.topic(), key=key_str, value=value_str))
        

def main():
    with open(r'/usr/src/data/data.csv') as f:
        csvreader = csv.DictReader(f, delimiter=',')
        count = 0
        for row in csvreader:
            producer.produce(topic=topic, value=json.dumps(row).encode('utf-8'), callback=delivery_callback)
            time.sleep(.2)
            count += 1

            if count == 1000:
                producer.poll()
        
        producer.flush()

if __name__ == '__main__':
    main()