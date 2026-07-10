import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('x23337818-dynamodb-fog-edge')

def delete_all_items():
    print("Deleting all items from table...")

    response = table.scan()
    data = response.get('Items', [])

    with table.batch_writer() as batch:
        for item in data:
            batch.delete_item(
                Key={
                    'timestamp': item['timestamp']
                }
            )

    print(f"Deleted {len(data)} items.")

    # Handle pagination (IMPORTANT for large tables)
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data = response.get('Items', [])

        with table.batch_writer() as batch:
            for item in data:
                batch.delete_item(
                    Key={
                        'timestamp': item['timestamp']
                    }
                )

        print(f"Deleted {len(data)} more items.")

    print("All items deleted successfully!")

if __name__ == "__main__":
    delete_all_items()