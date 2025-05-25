from kafka import KafkaProducer
import csv
import json
import time

producer = KafkaProducer(
    bootstrap_servers=['localhost:29092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

def send_csv_to_kafka(file_path, topic_name):
    with open(file_path, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            producer.send(topic_name, value=row)
            print(f"Sent: {row}")
            time.sleep(5)
    producer.flush()

if __name__ == '__main__':
    csv_file_path = '../data/financial_fraud_detection_dataset.csv'
    kafka_topic = 'Fraud_Detection'
    send_csv_to_kafka(csv_file_path, kafka_topic)
    print(f"Data from '{csv_file_path}' sent to Kafka topic '{kafka_topic}'.")