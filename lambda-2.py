import json
import boto3
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('x23337818-dynamodb-fog-edge')


#  Convert all floats → Decimal
def convert_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_decimal(i) for i in obj]
    else:
        return obj


def decimal_to_float(obj):
    if isinstance(obj, list):
        return [decimal_to_float(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj


def lambda_handler(event, context):
    print(" FULL EVENT RECEIVED:", json.dumps(event))

    method = event.get("httpMethod")
    if not method:
        method = event.get("requestContext", {}).get("http", {}).get("method")

    print(" METHOD:", method)

    # ---------------- STORE ----------------
    if method == "POST":
        try:
            raw_body = event.get("body")
            print(" RAW BODY:", raw_body)

            body = raw_body
            if isinstance(body, str):
                body = json.loads(body)

            print(" PARSED BODY:", body)

            #  FIX HERE
            body = convert_to_decimal(body)

            print(" AFTER DECIMAL CONVERSION:", body)

            item = {
                "timestamp": str(datetime.utcnow()),
                "temperature": body.get("temperature"),
                "humidity": body.get("humidity"),
                "cpu": body.get("cpu"),
                "air_quality": body.get("air_quality"),
                "pressure": body.get("pressure")
            }

            print(" ITEM TO STORE:", item)

            response = table.put_item(Item=item)

            print(" STORED SUCCESSFULLY:", response)

            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Stored successfully"})
            }

        except Exception as e:
            print(" ERROR IN LAMBDA-2:", str(e))
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e)})
            }

    # ---------------- FETCH ----------------
    elif method == "GET":
        try:
            response = table.scan()
            data = response.get("Items", [])

            print(" RAW DATA:", data)

            return {
                "statusCode": 200,
                "body": json.dumps(decimal_to_float(data))
            }

        except Exception as e:
            print(" ERROR FETCH:", str(e))
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e)})
            }

    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Invalid request"})
        }