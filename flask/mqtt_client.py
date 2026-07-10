import json
import threading
import time
import ssl
from datetime import datetime
import paho.mqtt.client as mqtt
import boto3
from decimal import Decimal

class MQTTDataClient:
    def __init__(self, broker_host, broker_port=8883, topics=None, use_aws_iot=True):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topics = topics or ["waste/processing/plant"]
        self.use_aws_iot = use_aws_iot
        self.client = None
        self.received_data = []
        self.max_data_points = 500
        self.is_connected = False
        self.latest_data = {}
        self.message_count = 0
        
        # Certificate paths for AWS IoT Core
        self.root_ca = "/home/ec2-user/environment/AmazonRootCA1.pem"
        self.private_key = "/home/ec2-user/environment/private.pem.key"
        self.certificate = "/home/ec2-user/environment/certificate.pem.crt"
        
        # For Lambda fallback
        self.use_lambda_fallback = True
        self.lambda_api_url = "https://69fnqucnuh.execute-api.us-east-1.amazonaws.com/default/lambda-2-x25105990"
        self.dynamodb_table = None
        
        # Initialize DynamoDB backup
        try:
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            self.dynamodb_table = dynamodb.Table('x25105990-dynamodb-table')
        except Exception as e:
            print(f"DynamoDB initialization failed: {e}")
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.is_connected = True
            print(f"✓ Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            # Subscribe to topics
            for topic in self.topics:
                client.subscribe(topic)
                print(f"✓ Subscribed to: {topic}")
        else:
            print(f"✗ Failed to connect to MQTT broker with code: {rc}")
            self.is_connected = False
    
    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode('utf-8')
            print(f"\n📨 Received MQTT message: {payload[:200]}...")
            
            data = json.loads(payload)
            
            # Add received timestamp
            data['received_timestamp'] = datetime.utcnow().isoformat()
            self.message_count += 1
            
            # Store in memory
            self.received_data.append(data)
            if len(self.received_data) > self.max_data_points:
                self.received_data = self.received_data[-self.max_data_points:]
            
            # Update latest data
            self.latest_data = data
            
            print(f"✅ Data from {data.get('device_id', 'Unknown')} - Status: {data.get('status', 'UNKNOWN')}")
            
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON received: {e}")
        except Exception as e:
            print(f"✗ Error processing message: {e}")
    
    def on_disconnect(self, client, userdata, rc):
        self.is_connected = False
        print(f"⚠️ Disconnected from MQTT broker (code: {rc})")
        # Try to reconnect
        if rc != 0:
            print("Attempting to reconnect...")
            try:
                client.connect(self.broker_host, self.broker_port, 60)
            except Exception as e:
                print(f"Reconnection failed: {e}")
    
    def store_in_dynamodb(self, data):
        """Store data in DynamoDB as backup"""
        if not self.dynamodb_table:
            return
        
        try:
            timestamp_str = data.get("timestamp", datetime.utcnow().isoformat())
            timestamp_dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            partition_key = f"{data.get('device_id', 'unknown')}_{timestamp_dt.strftime('%Y-%m-%d')}"
            
            item = {
                "device_date": partition_key,
                "timestamp": timestamp_str,
                "device_id": data.get("device_id"),
                "sensor_id": data.get("sensor_id"),
                "ph": Decimal(str(data.get("ph", 0))),
                "air_quality": int(data.get("air_quality", 0)),
                "temperature": Decimal(str(data.get("temperature", 0))),
                "weight": Decimal(str(data.get("weight", 0))),
                "pressure": Decimal(str(data.get("pressure", 0))),
                "gas": int(data.get("gas", 0)),
                "status": data.get("status", "UNKNOWN"),
                "critical_alerts": data.get("critical_alerts", []),
                "warning_alerts": data.get("warning_alerts", []),
                "processed_timestamp": datetime.utcnow().isoformat()
            }
            
            self.dynamodb_table.put_item(Item=item)
        except Exception as e:
            print(f"Failed to store in DynamoDB: {e}")
    
    def connect(self):
        """Connect to MQTT broker (AWS IoT Core or public)"""
        try:
            # Create client with VERSION1 for compatibility
            self.client = mqtt.Client(
                client_id="flask-dashboard-client",
                clean_session=True
            )
            
            # Set callbacks
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_disconnect = self.on_disconnect
            
            # Configure TLS for AWS IoT Core
            if self.use_aws_iot and self.broker_port == 8883:
                print("Configuring AWS IoT Core TLS...")
                self.client.tls_set(
                    ca_certs=self.root_ca,
                    certfile=self.certificate,
                    keyfile=self.private_key,
                    cert_reqs=ssl.CERT_REQUIRED,
                    tls_version=ssl.PROTOCOL_TLSv1_2
                )
            
            # Connect
            print(f"Connecting to {self.broker_host}:{self.broker_port}...")
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            
            # Wait for connection
            time.sleep(3)
            
            if self.is_connected:
                print("✓ MQTT client connected successfully")
                return True
            else:
                print("⚠️ MQTT client not connected after 3 seconds")
                # Try to force reconnect
                self.client.loop_stop()
                time.sleep(1)
                self.client.loop_start()
                time.sleep(2)
                return self.is_connected
            
        except Exception as e:
            print(f"✗ Failed to connect to MQTT broker: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.is_connected = False
    
    def get_latest_data(self):
        """Get the latest sensor reading"""
        return self.latest_data
    
    def get_recent_data(self, count=50):
        """Get recent sensor readings"""
        return self.received_data[-count:] if self.received_data else []
    
    def get_status(self):
        """Get connection status"""
        return {
            "connected": self.is_connected,
            "data_points": len(self.received_data),
            "latest_timestamp": self.latest_data.get("timestamp") if self.latest_data else None,
            "broker": self.broker_host,
            "topics": self.topics,
            "message_count": self.message_count
        }

def fetch_from_dynamodb(device_id=None, start_date=None, end_date=None, limit=100):
    """Direct fetch from DynamoDB as backup"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('x25105990-dynamodb-table')
        
        # Try to get latest records
        response = table.scan(Limit=limit)
        items = response.get("Items", [])
        
        # Sort by timestamp descending
        items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Convert Decimal to float
        def decimal_to_float(obj):
            if isinstance(obj, list):
                return [decimal_to_float(i) for i in obj]
            elif isinstance(obj, dict):
                return {k: decimal_to_float(v) for k, v in obj.items()}
            elif isinstance(obj, Decimal):
                return float(obj)
            else:
                return obj
        
        return decimal_to_float(items)
        
    except Exception as e:
        print(f"Error fetching from DynamoDB: {e}")
        import traceback
        traceback.print_exc()
        return []

def run_mqtt_client(broker_host="a14duv95cf46az-ats.iot.us-east-1.amazonaws.com", broker_port=8883):
    """Run the MQTT client"""
    client = MQTTDataClient(broker_host, broker_port, use_aws_iot=True)
    if client.connect():
        print("MQTT client started successfully")
        print(f"Listening to topics: {client.topics}")
        return client
    else:
        print("Failed to start MQTT client")
        return None

if __name__ == "__main__":
    # Test the client
    client = run_mqtt_client()
    
    if client:
        try:
            while True:
                time.sleep(5)
                status = client.get_status()
                print(f"Status: {status}")
        except KeyboardInterrupt:
            client.disconnect()
            print("MQTT client stopped")