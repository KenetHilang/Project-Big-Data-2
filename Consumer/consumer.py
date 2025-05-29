from kafka import KafkaConsumer
import time
import json
import os
import pandas as pd
from datetime import datetime

def main():
    batch = []
    batch_counter = 1
    
    output_dir = "../batch_data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    consumer = KafkaConsumer(
        'Fraud_Detection', 
        bootstrap_servers=['localhost:29092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='my-consumer-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    batch_time_limit = 300
    start_time = time.time()
    
    print("Consumer started. Collecting messages for 60-second batches...")
    
    # Consume messages in a loop
    for message in consumer:
        # Add the message to the current batch
        batch.append(message.value)
        
        # Print message info (optional, for debugging)
        print(f"Is it Fraud?: {message.value['is_fraud']}")
        
        # Check if it's time to process the batch
        current_time = time.time()
        if current_time - start_time >= batch_time_limit:
            # Process the batch
            process_batch(batch, batch_counter, output_dir)
            
            # Clear the batch and reset the timer
            batch = []
            start_time = current_time
            batch_counter += 1

def process_batch(batch, batch_num, output_dir):
    """
    Process a batch of messages and save to CSV
    """
    message_count = len(batch)
    print(f"\n--- Processing batch {batch_num} with {message_count} messages ---")
    
    if message_count == 0:
        print("Empty batch, skipping...")
        return
    
    # Convert batch to DataFrame
    df = pd.DataFrame(batch)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/batch_{batch_num}_{timestamp}.csv"
    
    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"Saved batch to: {filename}")
    
    print(f"Processed batch {batch_num} containing {message_count} messages")
    print("-----------------------------------\n")

if __name__ == "__main__":
    main()