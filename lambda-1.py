

import json
import urllib3

http = urllib3.PoolManager()

API_URL = "https://j2cosuv4ge.execute-api.us-east-1.amazonaws.com/default/x23389401-store-fetch-lambda"


def check_alert(data):
    alerts = []

    if data.get("temperature", 0) > 60:
        alerts.append("HIGH_TEMPERATURE")

    if data.get("humidity", 0) > 85:
        alerts.append("HIGH_HUMIDITY")

    if data.get("cpu", 0) > 90:
        alerts.append("HIGH_CPU")

    if data.get("air_quality", 0) > 300:
        alerts.append("POOR_AIR_QUALITY")

    if data.get("pressure", 0) < 950:
        alerts.append("LOW_PRESSURE")

    return alerts


def lambda_handler(event, context):
    print("FULL EVENT RECEIVED:", json.dumps(event))

    try:
        for record in event["Records"]:
            print("\n NEW SQS RECORD:", record)

            raw_body = record["body"]
            print(" RAW BODY:", raw_body)

            # Step 1: Parse body safely
            body = raw_body
            if isinstance(body, str):
                body = json.loads(body)

            # Step 2: Handle nested structures
            if "Message" in body:
                print(" Found SNS-style 'Message'")
                body = json.loads(body["Message"])

            if "message" in body:
                print(" Found nested 'message'")
                body = body["message"]

            print(" FINAL PARSED BODY:", body)

            # Step 3: Apply alert logic
            alerts = check_alert(body)

            # Step 4: Clean + convert types
            processed_data = {
                "temperature": float(body.get("temperature", 0)),
                "humidity": float(body.get("humidity", 0)),
                "cpu": float(body.get("cpu", 0)),
                "air_quality": int(body.get("air_quality", 0)),
                "pressure": float(body.get("pressure", 0)),
                "alert": True if alerts else False,
                "alert_types": alerts
            }

            print(" PROCESSED DATA:", processed_data)

            # Step 5: Send to Lambda-2
            response = http.request(
                "POST",
                API_URL,
                body=json.dumps(processed_data),
                headers={"Content-Type": "application/json"}
            )

            print(" API RESPONSE STATUS:", response.status)
            print(" API RESPONSE BODY:", response.data.decode())

        return {
            "statusCode": 200,
            "body": json.dumps("Processed successfully")
        }

    except Exception as e:
        print(" ERROR IN LAMBDA-1:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps(str(e))
        }