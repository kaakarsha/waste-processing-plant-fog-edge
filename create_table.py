import boto3
import time
import sys
from decimal import Decimal
from datetime import datetime
import random

def convert_to_decimal(obj):
    """Convert float to Decimal for DynamoDB"""
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_decimal(i) for i in obj]
    else:
        return obj

def create_dynamodb_table():
    """Create DynamoDB table for waste processing plant data"""
    
    # Initialize DynamoDB client
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')
    
    # Table configuration - USING THE CORRECT TABLE NAME
    table_name = 'x25105990-dynamodb-table'
    
    # Check if table already exists
    try:
        response = dynamodb.describe_table(TableName=table_name)
        print(f"Table '{table_name}' already exists.")
        print(f"Table Status: {response['Table']['TableStatus']}")
        return True
    except dynamodb.exceptions.ResourceNotFoundException:
        print(f"Table '{table_name}' does not exist. Creating...")
    
    try:
        # Create the table
        response = dynamodb.create_table(
            TableName=table_name,
            AttributeDefinitions=[
                {
                    'AttributeName': 'device_date',
                    'AttributeType': 'S'  # String type for partition key
                },
                {
                    'AttributeName': 'timestamp',
                    'AttributeType': 'S'  # String type for sort key
                }
            ],
            KeySchema=[
                {
                    'AttributeName': 'device_date',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'timestamp',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            BillingMode='PAY_PER_REQUEST',  # On-demand pricing
            Tags=[
                {
                    'Key': 'Project',
                    'Value': 'WasteProcessingPlant'
                },
                {
                    'Key': 'Environment',
                    'Value': 'Production'
                }
            ]
        )
        
        print(f"Table '{table_name}' creation initiated.")
        print(f"Table ARN: {response['TableDescription']['TableArn']}")
        
        # Wait for table to become active
        print("Waiting for table to become active...")
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name, WaiterConfig={'Delay': 5, 'MaxAttempts': 60})
        
        # Verify table status
        response = dynamodb.describe_table(TableName=table_name)
        status = response['Table']['TableStatus']
        print(f"Table Status: {status}")
        
        return status == 'ACTIVE'
        
    except Exception as e:
        print(f"Error creating table: {e}")
        return False

def create_secondary_indexes():
    """Create Global Secondary Indexes (GSI) one at a time to avoid limit issues"""
    
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')
    table_name = 'x25105990-dynamodb-table'
    
    try:
        print("Creating Global Secondary Indexes one at a time...")
        
        # GSI 1: Query by device_id and timestamp
        print("Creating index: device_id-timestamp-index...")
        response = dynamodb.update_table(
            TableName=table_name,
            AttributeDefinitions=[
                {
                    'AttributeName': 'device_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'timestamp',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexUpdates=[
                {
                    'Create': {
                        'IndexName': 'device_id-timestamp-index',
                        'KeySchema': [
                            {
                                'AttributeName': 'device_id',
                                'KeyType': 'HASH'
                            },
                            {
                                'AttributeName': 'timestamp',
                                'KeyType': 'RANGE'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    }
                }
            ]
        )
        
        print("Index creation initiated. Waiting 30 seconds...")
        time.sleep(30)
        
        # Check first index status
        response = dynamodb.describe_table(TableName=table_name)
        indexes = response['Table'].get('GlobalSecondaryIndexes', [])
        for idx in indexes:
            if idx['IndexName'] == 'device_id-timestamp-index':
                print(f"Index: {idx['IndexName']} - Status: {idx['IndexStatus']}")
                break
        
        # GSI 2: Query by status and timestamp
        print("\nCreating index: status-index...")
        response = dynamodb.update_table(
            TableName=table_name,
            AttributeDefinitions=[
                {
                    'AttributeName': 'status',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'timestamp',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexUpdates=[
                {
                    'Create': {
                        'IndexName': 'status-index',
                        'KeySchema': [
                            {
                                'AttributeName': 'status',
                                'KeyType': 'HASH'
                            },
                            {
                                'AttributeName': 'timestamp',
                                'KeyType': 'RANGE'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    }
                }
            ]
        )
        
        print("Index creation initiated. Waiting 30 seconds...")
        time.sleep(30)
        
        # Verify all indexes
        response = dynamodb.describe_table(TableName=table_name)
        indexes = response['Table'].get('GlobalSecondaryIndexes', [])
        
        print("\nAll Indexes:")
        for idx in indexes:
            print(f"  - {idx['IndexName']} - Status: {idx['IndexStatus']}")
        
        return True
        
    except Exception as e:
        print(f"Error creating secondary indexes: {e}")
        return False

def describe_table():
    """Describe the table structure and indexes"""
    
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')
    table_name = 'x25105990-dynamodb-table'
    
    try:
        response = dynamodb.describe_table(TableName=table_name)
        table = response['Table']
        
        print("\n" + "=" * 60)
        print("TABLE DETAILS")
        print("=" * 60)
        print(f"Table Name: {table['TableName']}")
        print(f"Table Status: {table['TableStatus']}")
        print(f"Creation Date: {table['CreationDateTime']}")
        print(f"Table ARN: {table['TableArn']}")
        print(f"Table Size: {table.get('TableSizeBytes', 0)} bytes")
        print(f"Item Count: {table.get('ItemCount', 0)}")
        
        print("\nKEY SCHEMA:")
        for key in table['KeySchema']:
            print(f"  - {key['AttributeName']} ({key['KeyType']})")
        
        print("\nATTRIBUTES:")
        for attr in table['AttributeDefinitions']:
            print(f"  - {attr['AttributeName']} ({attr['AttributeType']})")
        
        print("\nGLOBAL SECONDARY INDEXES:")
        if 'GlobalSecondaryIndexes' in table:
            for idx in table['GlobalSecondaryIndexes']:
                print(f"  - {idx['IndexName']}")
                print(f"    Status: {idx['IndexStatus']}")
                print(f"    Size: {idx.get('IndexSizeBytes', 0)} bytes")
                print(f"    Items: {idx.get('ItemCount', 0)}")
        else:
            print("  No GSI found.")
        
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"Error describing table: {e}")
        return False

def create_sample_data():
    """Add sample data for testing"""
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('x25105990-dynamodb-table')
    
    print("\nAdding sample data...")
    
    devices = ['WASTE_PLANT_01', 'WASTE_PLANT_02', 'WASTE_PLANT_03']
    statuses = ['NORMAL', 'WARNING', 'CRITICAL']
    
    added_count = 0
    
    for i in range(10):
        for device in devices:
            timestamp = datetime.utcnow().isoformat()
            partition_key = f"{device}_{datetime.utcnow().strftime('%Y-%m-%d')}"
            
            # Random status with some critical/warning
            status = random.choices(statuses, weights=[0.7, 0.2, 0.1])[0]
            
            # Adjust values based on status
            if status == 'NORMAL':
                ph = Decimal(str(round(random.uniform(6.5, 7.5), 2)))
                air_quality = random.randint(60, 120)
                temperature = Decimal(str(round(random.uniform(30, 40), 1)))
                weight = Decimal(str(round(random.uniform(1000, 4000), 2)))
                pressure = Decimal(str(round(random.uniform(990, 1010), 1)))
                gas = random.randint(150, 350)
                critical_alerts = []
                warning_alerts = []
            elif status == 'WARNING':
                ph = Decimal(str(round(random.uniform(5.0, 5.8), 2)))
                air_quality = random.randint(180, 220)
                temperature = Decimal(str(round(random.uniform(50, 58), 1)))
                weight = Decimal(str(round(random.uniform(5000, 6000), 2)))
                pressure = Decimal(str(round(random.uniform(1025, 1035), 1)))
                gas = random.randint(600, 750)
                critical_alerts = []
                warning_alerts = [
                    {
                        "sensor": "temperature",
                        "value": float(temperature),
                        "threshold_min": 10,
                        "threshold_max": 60,
                        "severity": "WARNING"
                    }
                ]
            else:  # CRITICAL
                ph = Decimal(str(round(random.uniform(2.5, 4.0), 2)))
                air_quality = random.randint(280, 350)
                temperature = Decimal(str(round(random.uniform(65, 75), 1)))
                weight = Decimal(str(round(random.uniform(7000, 8500), 2)))
                pressure = Decimal(str(round(random.uniform(1045, 1060), 1)))
                gas = random.randint(900, 1100)
                critical_alerts = [
                    {
                        "sensor": "temperature",
                        "value": float(temperature),
                        "threshold_min": 0,
                        "threshold_max": 70,
                        "severity": "CRITICAL"
                    },
                    {
                        "sensor": "gas",
                        "value": float(gas),
                        "threshold_min": 0,
                        "threshold_max": 1000,
                        "severity": "CRITICAL"
                    }
                ]
                warning_alerts = []
            
            # Build item with proper Decimal types
            item = {
                'device_date': partition_key,
                'timestamp': timestamp,
                'device_id': device,
                'sensor_id': 'SENSOR_NODE_01',
                'ph': ph,
                'air_quality': air_quality,
                'temperature': temperature,
                'weight': weight,
                'pressure': pressure,
                'gas': gas,
                'status': status,
                'critical_alerts': critical_alerts,
                'warning_alerts': warning_alerts,
                'processed_timestamp': datetime.utcnow().isoformat()
            }
            
            try:
                table.put_item(Item=item)
                added_count += 1
                print(f"Added record {added_count} for device {device}")
            except Exception as e:
                print(f"Error adding item: {e}")
                print(f"Item: {item}")
    
    print(f"\nSample data added successfully! Added {added_count} records.")
    return True

def delete_table():
    """Delete the table (use with caution)"""
    
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')
    table_name = 'x25105990-dynamodb-table'
    
    try:
        response = dynamodb.delete_table(TableName=table_name)
        print(f"Table '{table_name}' deletion initiated.")
        print(f"Table ARN: {response['TableDescription']['TableArn']}")
        return True
    except Exception as e:
        print(f"Error deleting table: {e}")
        return False

def main():
    """Main execution function"""
    
    print("=" * 60)
    print("DynamoDB Table Creation Utility")
    print("Waste Processing Plant Monitoring System")
    print("=" * 60)
    
    # Show menu
    print("\nOptions:")
    print("1. Create/Describe Table")
    print("2. Delete Table (Warning: This will remove all data)")
    print("3. Add Sample Data")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == '1':
        # Create table
        print("\n[Step 1] Creating DynamoDB Table...")
        if create_dynamodb_table():
            print("✓ Table created successfully")
        else:
            print("✗ Table creation failed")
            sys.exit(1)
        
        # Create secondary indexes one at a time
        print("\n[Step 2] Creating Secondary Indexes...")
        if create_secondary_indexes():
            print("✓ Secondary indexes created successfully")
        else:
            print("✗ Secondary index creation failed")
            print("  Note: You can run option 3 to add sample data without indexes.")
        
        # Describe table
        print("\n[Step 3] Describing Table...")
        describe_table()
        
        # Add sample data (optional)
        print("\n[Step 4] Adding Sample Data...")
        add_sample = input("Do you want to add sample data for testing? (y/n): ")
        if add_sample.lower() == 'y':
            create_sample_data()
    
    elif choice == '2':
        print("\n⚠️  WARNING: This will delete the entire table and all data!")
        confirm = input("Are you sure you want to continue? (yes/no): ")
        if confirm.lower() == 'yes':
            delete_table()
        else:
            print("Table deletion cancelled.")
    
    elif choice == '3':
        print("\nAdding Sample Data...")
        create_sample_data()
    
    elif choice == '4':
        print("Exiting...")
        sys.exit(0)
    
    else:
        print("Invalid choice. Exiting...")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nTable Name: x25105990-dynamodb-table")
    print("Region: us-east-1")
    print("\nTo query the table:")
    print("  aws dynamodb scan --table-name x25105990-dynamodb-table --region us-east-1")
    print("")
    print("To get latest records for a device:")
    print("  aws dynamodb query --table-name x25105990-dynamodb-table \\")
    print("    --key-condition-expression 'device_date = :device_date' \\")
    print("    --expression-attribute-values '{':device_date': {'S': 'WASTE_PLANT_01_2026-07-09'}}' \\")
    print("    --scan-index-forward false --limit 10")
    print("")
    print("To delete the table:")
    print("  aws dynamodb delete-table --table-name x25105990-dynamodb-table --region us-east-1")
    print("=" * 60)

if __name__ == "__main__":
    main()