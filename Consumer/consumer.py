from kafka import KafkaConsumer
import time
import json

def main():
    batch = []
    
    consumer = KafkaConsumer(
        'Fraud_Detection', 
        bootstrap_servers=['localhost:29092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='my-consumer-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    batch_time_limit = 60
    start_time = time.time()
    
    print("Consumer started. Collecting messages for 60-second batches...")
    
    # Consume messages in a loop
    for message in consumer:
        # Add the message to the current batch
        batch.append(message.value)
        
        # Print message info (optional, for debugging)
        print(f"Received: {message.value}")
        
        # Check if it's time to process the batch
        current_time = time.time()
        if current_time - start_time >= batch_time_limit:
            # Process the batch
            process_batch(batch)
            
            # Clear the batch and reset the timer
            batch = []
            start_time = current_time

def process_batch(batch):
    """
    Process a batch of messages
    """
    message_count = len(batch)
    print(f"\n--- Processing batch of {message_count} messages ---")
    
    # Here you would typically:
    # 1. Transform the data
    # 2. Save to database
    # 3. Generate analytics
    # 4. etc.
    
    # For this example, we'll just print the number of messages
    print(f"Processed batch containing {message_count} messages")
    print("-----------------------------------\n")

if __name__ == "__main__":
    main()