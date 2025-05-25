# Project-Big-Data-2: Fraud Detection with Kafka

This project implements a fraud detection system using Apache Kafka for real-time data streaming.

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Required Python packages: `kafka-python`

## Setup Instructions

### 1. Start Kafka Environment

Start the Kafka and ZooKeeper containers using Docker Compose:

```bash
docker-compose up -d
```

This will start:
- ZooKeeper (localhost:2181)
- Kafka (localhost:9092)
- Kafka UI (localhost:8080) - Optional web interface to monitor Kafka

### 2. Verify Kafka is Running

You can check if the containers are running:

```bash
docker ps
```

You can also visit the Kafka UI at http://localhost:8080 in your browser.

### 3. Prepare Your Data

Make sure your CSV file is available. The default name is `financial_fraud_detection_dataset.csv` and it should be placed in the project root.

### 4. Run the Consumer

Open a terminal and start the consumer:

```bash
python Consumer/consumer.py
```

The consumer will start and wait for messages.

### 5. Run the Producer

Open another terminal and start the producer:

```bash
python Producer/producer.py
```

Or specify a different CSV file:

```bash
python Producer/producer.py path/to/your/data.csv
```

## Project Structure

- `docker-compose.yml`: Docker configuration for Kafka and ZooKeeper
- `Producer/producer.py`: Sends data from CSV to Kafka topic
- `Consumer/consumer.py`: Receives and processes data from Kafka topic

## Stopping the Services

To stop the Kafka environment:

```bash
docker-compose down
```

## Troubleshooting

1. **Connection Issues**:
   - Ensure Docker containers are running
   - Check that ports 9092 and 2181 are not being used by other applications

2. **CSV File Not Found**:
   - Verify the path to your CSV file
   - Make sure the CSV file has the correct permissions

3. **Message Format Issues**:
   - Ensure your CSV has headers
   - Check that the consumer can deserialize the messages sent by the producer