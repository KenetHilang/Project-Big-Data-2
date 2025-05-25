# Project-Big-Data-2: Fraud Detection with Kafka

## Group's Members
| Name (Nama)           | Student ID (NRP)   |
|----------------|--------------|
| Rafael Jonathan Arnoldus  | 5027231006     |
| Michael Kenneth Salim      | 5027231008     |
| Nicholas Arya Kris Nugroho      | 5027231058     |


This project implements a fraud detection system using Apache Kafka and Pyspark simulating real-time data streaming.

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- UV for python packages
   - use `pip install uv` to install uv, and then proceed with `uv sync`
- Required Python packages: `kafka-python`

**Dataset**: https://www.kaggle.com/datasets/aryan208/financial-transactions-dataset-for-fraud-detection

## Setup Instructions

### 1. Start Kafka Environment

Start the Kafka and ZooKeeper containers using Docker Compose:

```bash
docker-compose up -d
```

This will start:
- ZooKeeper (localhost:22181)
- Kafka (localhost:29092)


### 2. Verify Kafka is Running

You can check if the containers are running:

```bash
docker ps
```

### 3. Prepare Your Data

Make sure your CSV file is available. The default name is `financial_fraud_detection_dataset.csv` and it should be placed in the data directory.

### 4. Run the Consumer

Open a terminal and start the consumer:

```bash
uv run Consumer/consumer.py
```

The consumer will start and wait for messages.

### 5. Run the Producer

Open another terminal and start the producer:

```bash
uv run Producer/producer.py
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
   - Check that ports 29092 and 22181 are not being used by other applications

2. **CSV File Not Found**:
   - Verify the path to your CSV file
   - Make sure the CSV file has the correct permissions

3. **Message Format Issues**:
   - Ensure your CSV has headers
   - Check that the consumer can deserialize the messages sent by the producer