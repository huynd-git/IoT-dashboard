from confluent_kafka import Consumer, KafkaError
import psycopg2
from psycopg2.extensions import AsIs
import os
import json
import time

"""VARIABLES AND CONFIGURATION"""
topic = "transformed-data"
table_name = 'iot.transformed_network_flows'

# Consumer configuration
conf = {
    "bootstrap.servers": "kafka-broker:9092",
    "group.id": "ld-gr1",
    "auto.offset.reset": "earliest"
}

"""QUERIES"""
insert_query = """
INSERT INTO {} (
    timestamp, src_ip, dst_ip, protocol, totlen_fwd_pkts, totlen_bwd_pkts, 
    flow_duration, tot_fwd_pkts, tot_bwd_pkts, hour, day, week, 
    src_latitude, src_longitude, src_city, src_country, 
    dst_latitude, dst_longitude, dst_city, dst_country, 
    total_data_transferred, data_transfer_rate, packet_rate
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
""".format(table_name)


"""HELPER FUNCTIONS"""
def get_conn():
    """
    Create a connection to PostgreSQL data base using environmental variables

    Return: psql connection and cursor
    """
    db_name = os.getenv('POSTGRES_DB')
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_host = os.getenv('POSTGRES_HOST')
    db_port = os.getenv('POSTGRES_PORT')


    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host, 
        port=db_port
    )


    cur = conn.cursor()
    return conn, cur


def main():
    consumer = Consumer(conf)
    consumer.subscribe([topic])

    # Connect to PostgreSQL
    conn, cur = get_conn()
    try:
        time.sleep(100)    # wait for the psql database and kafka server start up completly

        # Consume messages from Kafka
        while True:
            msg = consumer.poll(1.0)    # Poll for new messages with a timeout of 1 second

            if msg is None:
                continue
            # Error handling
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print('Reached end of partition')
                else:
                    print(f'Error while consuming message: {msg.error()}')
            else:
                # Parse the JSON message value
                data = json.loads(msg.value())

                # Handle "None" value in the record
                for key, value in data.items():
                    if value is None:
                        data[key] = AsIs('NULL')

                # Extract values for the SQL query
                values = (
                    data['Timestamp'], data['Src IP'], data['Dst IP'], data['Protocol'],
                    data['TotLen Fwd Pkts'], data['TotLen Bwd Pkts'], data['Flow Duration'],
                    data['Tot Fwd Pkts'], data['Tot Bwd Pkts'], data['hour'], data['day'], data['week'],
                    data['Src_Latitude'], data['Src_Longtidude'], data['Src_City'], data['Src_Country'],
                    data['Dst_Latitude'], data['Dst_Longtidude'], data['Dst_City'], data['Dst_Country'],
                    data['Total_Data_Transferred'], data['Data_Transfer_Rate'], data['Packet_Rate']
                )

                # Execute the insert query
                print("Inserting data ...")
                cur.execute(insert_query, values)
                conn.commit()  # Commit the transaction

    except KeyboardInterrupt:
        pass
    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()
        # Close the Kafka consumer
        consumer.close()


if __name__ == "__main__":
    main()