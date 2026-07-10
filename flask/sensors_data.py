# import json
# import time
# import random
# from datetime import datetime
# import paho.mqtt.client as mqtt

# # Configuration
# MQTT_BROKER = "test.mosquitto.org"  # Public MQTT broker for testing
# MQTT_PORT = 1883
# MQTT_TOPIC = "waste/processing/plant"
# CLIENT_ID = "iot-core-thing-x25105990"

# class WasteSensorSimulator:
#     def __init__(self):
#         self.device_id = "WASTE_PLANT_01"
#         self.sensor_id = "SENSOR_NODE_01"
        
#         # Normal operating ranges for waste processing plant
#         self.ranges = {
#             "ph": {"min": 6.0, "max": 8.0},
#             "air_quality": {"min": 50, "max": 150},
#             "temperature": {"min": 25, "max": 45},
#             "weight": {"min": 500, "max": 5000},
#             "pressure": {"min": 980, "max": 1020},
#             "gas": {"min": 100, "max": 500}
#         }
        
#         # Critical threshold definitions
#         self.critical_thresholds = {
#             "ph": {"min": 4.0, "max": 9.5},
#             "air_quality": {"min": 0, "max": 300},
#             "temperature": {"min": 0, "max": 70},
#             "weight": {"min": 100, "max": 8000},
#             "pressure": {"min": 950, "max": 1050},
#             "gas": {"min": 0, "max": 1000}
#         }
        
#         # Warning thresholds
#         self.warning_thresholds = {
#             "ph": {"min": 5.0, "max": 9.0},
#             "air_quality": {"min": 0, "max": 200},
#             "temperature": {"min": 10, "max": 60},
#             "weight": {"min": 200, "max": 7000},
#             "pressure": {"min": 960, "max": 1040},
#             "gas": {"min": 0, "max": 800}
#         }
    
#     def generate_sensor_data(self):
#         """Generate realistic sensor data for waste processing plant"""
#         anomaly_chance = random.random()
        
#         if anomaly_chance < 0.05:  # 5% chance of critical anomaly
#             return self.generate_critical_anomaly()
#         elif anomaly_chance < 0.15:  # 10% chance of warning
#             return self.generate_warning_data()
#         else:  # 85% normal operation
#             return self.generate_normal_data()
    
#     def generate_normal_data(self):
#         """Generate normal sensor readings"""
#         return {
#             "device_id": self.device_id,
#             "sensor_id": self.sensor_id,
#             "timestamp": datetime.utcnow().isoformat(),
#             "ph": round(random.uniform(6.5, 7.5), 2),
#             "air_quality": random.randint(60, 120),
#             "temperature": round(random.uniform(30, 40), 1),
#             "weight": round(random.uniform(1000, 4000), 2),
#             "pressure": round(random.uniform(990, 1010), 1),
#             "gas": random.randint(150, 350),
#             "status": "NORMAL"
#         }
    
#     def generate_warning_data(self):
#         """Generate warning-level sensor readings"""
#         warning_scenario = random.choice([
#             "high_temp", "low_ph", "high_gas", "high_pressure", "high_air_quality"
#         ])
        
#         base_data = self.generate_normal_data()
        
#         if warning_scenario == "high_temp":
#             base_data["temperature"] = round(random.uniform(50, 58), 1)
#             base_data["status"] = "WARNING"
#         elif warning_scenario == "low_ph":
#             base_data["ph"] = round(random.uniform(4.5, 5.5), 2)
#             base_data["status"] = "WARNING"
#         elif warning_scenario == "high_gas":
#             base_data["gas"] = random.randint(600, 750)
#             base_data["status"] = "WARNING"
#         elif warning_scenario == "high_pressure":
#             base_data["pressure"] = round(random.uniform(1025, 1035), 1)
#             base_data["status"] = "WARNING"
#         elif warning_scenario == "high_air_quality":
#             base_data["air_quality"] = random.randint(180, 220)
#             base_data["status"] = "WARNING"
        
#         return base_data
    
#     def generate_critical_anomaly(self):
#         """Generate critical-level sensor readings"""
#         critical_scenario = random.choice([
#             "extreme_high_temp", "extreme_low_ph", "extreme_high_gas", 
#             "extreme_high_pressure", "extreme_high_air_quality", "extreme_weight"
#         ])
        
#         base_data = self.generate_normal_data()
        
#         if critical_scenario == "extreme_high_temp":
#             base_data["temperature"] = round(random.uniform(65, 75), 1)
#             base_data["status"] = "CRITICAL"
#         elif critical_scenario == "extreme_low_ph":
#             base_data["ph"] = round(random.uniform(2.5, 4.0), 2)
#             base_data["status"] = "CRITICAL"
#         elif critical_scenario == "extreme_high_gas":
#             base_data["gas"] = random.randint(900, 1100)
#             base_data["status"] = "CRITICAL"
#         elif critical_scenario == "extreme_high_pressure":
#             base_data["pressure"] = round(random.uniform(1045, 1060), 1)
#             base_data["status"] = "CRITICAL"
#         elif critical_scenario == "extreme_high_air_quality":
#             base_data["air_quality"] = random.randint(280, 350)
#             base_data["status"] = "CRITICAL"
#         elif critical_scenario == "extreme_weight":
#             base_data["weight"] = round(random.uniform(7000, 8500), 2)
#             base_data["status"] = "CRITICAL"
        
#         return base_data
    
#     def validate_data(self, data):
#         """Validate sensor data against critical thresholds"""
#         validation_results = {
#             "valid": True,
#             "critical_alerts": [],
#             "warning_alerts": []
#         }
        
#         for sensor, value in data.items():
#             if sensor in ["device_id", "sensor_id", "timestamp", "status"]:
#                 continue
                
#             if sensor in self.critical_thresholds:
#                 thresholds = self.critical_thresholds[sensor]
#                 if thresholds["min"] > value or value > thresholds["max"]:
#                     validation_results["valid"] = False
#                     validation_results["critical_alerts"].append(
#                         f"{sensor} critical: {value} (threshold: {thresholds['min']}-{thresholds['max']})"
#                     )
            
#             if sensor in self.warning_thresholds:
#                 thresholds = self.warning_thresholds[sensor]
#                 if thresholds["min"] > value or value > thresholds["max"]:
#                     validation_results["warning_alerts"].append(
#                         f"{sensor} warning: {value} (threshold: {thresholds['min']}-{thresholds['max']})"
#                     )
        
#         return validation_results

# # MQTT Callback functions
# def on_connect(client, userdata, flags, rc, properties=None):
#     if rc == 0:
#         print("Connected to MQTT broker successfully")
#     else:
#         print(f"Failed to connect to MQTT broker with code: {rc}")

# def on_publish(client, userdata, mid, reason_code=None, properties=None):
#     print(f"Message {mid} published successfully")

# def on_disconnect(client, userdata, rc, properties=None):
#     print("Disconnected from MQTT broker")

# def publish_sensor_data(mqtt_client, topic, data):
#     """Publish sensor data to MQTT topic"""
#     try:
#         payload = json.dumps(data)
#         result = mqtt_client.publish(topic, payload, qos=1)
#         if result.rc == mqtt.MQTT_ERR_SUCCESS:
#             return True
#         else:
#             print(f"Failed to publish message: {result.rc}")
#             return False
#     except Exception as e:
#         print(f"Error publishing message: {e}")
#         return False

# def main():
#     # Initialize MQTT client with callback API version
#     # This is the fix for the version 2.0+ compatibility
#     mqtt_client = mqtt.Client(
#         client_id=CLIENT_ID,
#         callback_api_version=mqtt.CallbackAPIVersion.VERSION2
#     )
    
#     # Assign callback functions
#     mqtt_client.on_connect = on_connect
#     mqtt_client.on_publish = on_publish
#     mqtt_client.on_disconnect = on_disconnect
    
#     # Connect to MQTT broker
#     try:
#         mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
#         mqtt_client.loop_start()
#         print(f"Connecting to {MQTT_BROKER}:{MQTT_PORT}...")
#     except Exception as e:
#         print(f"Failed to connect to MQTT broker: {e}")
#         return
    
#     # Initialize simulator
#     simulator = WasteSensorSimulator()
    
#     print("=" * 60)
#     print("Waste Processing Plant Sensor Simulator")
#     print("=" * 60)
#     print(f"Device ID: {simulator.device_id}")
#     print(f"Sensor ID: {simulator.sensor_id}")
#     print(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
#     print(f"MQTT Topic: {MQTT_TOPIC}")
#     print("=" * 60)
    
#     message_count = 0
#     normal_count = 0
#     warning_count = 0
#     critical_count = 0
    
#     try:
#         while True:
#             message_count += 1
            
#             # Generate sensor data
#             sensor_data = simulator.generate_sensor_data()
            
#             # Validate data
#             validation = simulator.validate_data(sensor_data)
            
#             # Update status based on validation
#             if validation["critical_alerts"]:
#                 sensor_data["status"] = "CRITICAL"
#                 critical_count += 1
#             elif validation["warning_alerts"]:
#                 sensor_data["status"] = "WARNING"
#                 warning_count += 1
#             else:
#                 normal_count += 1
            
#             # Add validation results to data
#             sensor_data["critical_alerts"] = validation["critical_alerts"]
#             sensor_data["warning_alerts"] = validation["warning_alerts"]
            
#             # Publish to MQTT
#             success = publish_sensor_data(mqtt_client, MQTT_TOPIC, sensor_data)
            
#             if success:
#                 print(f"\n[Message #{message_count}]")
#                 print(f"Timestamp: {sensor_data['timestamp']}")
#                 print(f"Status: {sensor_data['status']}")
#                 print(f"pH: {sensor_data['ph']}")
#                 print(f"Air Quality: {sensor_data['air_quality']}")
#                 print(f"Temperature: {sensor_data['temperature']}C")
#                 print(f"Weight: {sensor_data['weight']}kg")
#                 print(f"Pressure: {sensor_data['pressure']}hPa")
#                 print(f"Gas: {sensor_data['gas']}ppm")
                
#                 if validation["warning_alerts"]:
#                     print("\nWarning Alerts:")
#                     for alert in validation["warning_alerts"]:
#                         print(f"  - {alert}")
                
#                 if validation["critical_alerts"]:
#                     print("\nCritical Alerts:")
#                     for alert in validation["critical_alerts"]:
#                         print(f"  - {alert}")
            
#             # Print statistics every 10 messages
#             if message_count % 10 == 0:
#                 total = normal_count + warning_count + critical_count
#                 print(f"\n[Statistics - Last {total} messages]")
#                 print(f"  Normal: {normal_count} ({normal_count/total*100:.1f}%)")
#                 print(f"  Warning: {warning_count} ({warning_count/total*100:.1f}%)")
#                 print(f"  Critical: {critical_count} ({critical_count/total*100:.1f}%)")
#                 print("-" * 40)
            
#             # Wait 3 seconds before next reading
#             time.sleep(3)
            
#     except KeyboardInterrupt:
#         print("\n" + "=" * 60)
#         print(f"Simulator stopped. Total messages sent: {message_count}")
#         print(f"Final Statistics: Normal={normal_count}, Warning={warning_count}, Critical={critical_count}")
#         print("=" * 60)
#         mqtt_client.loop_stop()
#         mqtt_client.disconnect()
#         print("Disconnected from MQTT broker")

# if __name__ == "__main__":
#     main()


import json
import time
import random
import ssl
from datetime import datetime
import paho.mqtt.client as mqtt

# ==================== AWS IoT Core Configuration ====================
AWS_IOT_ENDPOINT = "a14duv95cf46az-ats.iot.us-east-1.amazonaws.com"
AWS_IOT_PORT = 8883
AWS_IOT_TOPIC = "waste/processing/plant"
CLIENT_ID = "iot-core-thing-x25105990"

# Certificate paths - UPDATE THESE PATHS
ROOT_CA = "/home/ec2-user/environment/AmazonRootCA1.pem"
PRIVATE_KEY = "/home/ec2-user/environment/private.pem.key"
CERTIFICATE = "/home/ec2-user/environment/certificate.pem.crt"

# ==================== Configuration ====================
# If you want to test with public broker instead, set USE_AWS_IOT = False
USE_AWS_IOT = True  # Set to False to use public test broker

# Public MQTT broker (fallback)
PUBLIC_MQTT_BROKER = "test.mosquitto.org"
PUBLIC_MQTT_PORT = 1883

# ==========================================================

class WasteSensorSimulator:
    def __init__(self):
        self.device_id = "WASTE_PLANT_01"
        self.sensor_id = "SENSOR_NODE_01"
        
        # Normal operating ranges for waste processing plant
        self.ranges = {
            "ph": {"min": 6.0, "max": 8.0},
            "air_quality": {"min": 50, "max": 150},
            "temperature": {"min": 25, "max": 45},
            "weight": {"min": 500, "max": 5000},
            "pressure": {"min": 980, "max": 1020},
            "gas": {"min": 100, "max": 500}
        }
        
        # Critical threshold definitions
        self.critical_thresholds = {
            "ph": {"min": 4.0, "max": 9.5},
            "air_quality": {"min": 0, "max": 300},
            "temperature": {"min": 0, "max": 70},
            "weight": {"min": 100, "max": 8000},
            "pressure": {"min": 950, "max": 1050},
            "gas": {"min": 0, "max": 1000}
        }
        
        # Warning thresholds
        self.warning_thresholds = {
            "ph": {"min": 5.0, "max": 9.0},
            "air_quality": {"min": 0, "max": 200},
            "temperature": {"min": 10, "max": 60},
            "weight": {"min": 200, "max": 7000},
            "pressure": {"min": 960, "max": 1040},
            "gas": {"min": 0, "max": 800}
        }
    
    def generate_sensor_data(self):
        """Generate realistic sensor data for waste processing plant"""
        anomaly_chance = random.random()
        
        if anomaly_chance < 0.05:  # 5% chance of critical anomaly
            return self.generate_critical_anomaly()
        elif anomaly_chance < 0.15:  # 10% chance of warning
            return self.generate_warning_data()
        else:  # 85% normal operation
            return self.generate_normal_data()
    
    def generate_normal_data(self):
        """Generate normal sensor readings"""
        return {
            "device_id": self.device_id,
            "sensor_id": self.sensor_id,
            "timestamp": datetime.utcnow().isoformat(),
            "ph": round(random.uniform(6.5, 7.5), 2),
            "air_quality": random.randint(60, 120),
            "temperature": round(random.uniform(30, 40), 1),
            "weight": round(random.uniform(1000, 4000), 2),
            "pressure": round(random.uniform(990, 1010), 1),
            "gas": random.randint(150, 350),
            "status": "NORMAL"
        }
    
    def generate_warning_data(self):
        """Generate warning-level sensor readings"""
        warning_scenario = random.choice([
            "high_temp", "low_ph", "high_gas", "high_pressure", "high_air_quality"
        ])
        
        base_data = self.generate_normal_data()
        
        if warning_scenario == "high_temp":
            base_data["temperature"] = round(random.uniform(50, 58), 1)
            base_data["status"] = "WARNING"
        elif warning_scenario == "low_ph":
            base_data["ph"] = round(random.uniform(4.5, 5.5), 2)
            base_data["status"] = "WARNING"
        elif warning_scenario == "high_gas":
            base_data["gas"] = random.randint(600, 750)
            base_data["status"] = "WARNING"
        elif warning_scenario == "high_pressure":
            base_data["pressure"] = round(random.uniform(1025, 1035), 1)
            base_data["status"] = "WARNING"
        elif warning_scenario == "high_air_quality":
            base_data["air_quality"] = random.randint(180, 220)
            base_data["status"] = "WARNING"
        
        return base_data
    
    def generate_critical_anomaly(self):
        """Generate critical-level sensor readings"""
        critical_scenario = random.choice([
            "extreme_high_temp", "extreme_low_ph", "extreme_high_gas", 
            "extreme_high_pressure", "extreme_high_air_quality", "extreme_weight"
        ])
        
        base_data = self.generate_normal_data()
        
        if critical_scenario == "extreme_high_temp":
            base_data["temperature"] = round(random.uniform(65, 75), 1)
            base_data["status"] = "CRITICAL"
        elif critical_scenario == "extreme_low_ph":
            base_data["ph"] = round(random.uniform(2.5, 4.0), 2)
            base_data["status"] = "CRITICAL"
        elif critical_scenario == "extreme_high_gas":
            base_data["gas"] = random.randint(900, 1100)
            base_data["status"] = "CRITICAL"
        elif critical_scenario == "extreme_high_pressure":
            base_data["pressure"] = round(random.uniform(1045, 1060), 1)
            base_data["status"] = "CRITICAL"
        elif critical_scenario == "extreme_high_air_quality":
            base_data["air_quality"] = random.randint(280, 350)
            base_data["status"] = "CRITICAL"
        elif critical_scenario == "extreme_weight":
            base_data["weight"] = round(random.uniform(7000, 8500), 2)
            base_data["status"] = "CRITICAL"
        
        return base_data
    
    def validate_data(self, data):
        """Validate sensor data against critical thresholds"""
        validation_results = {
            "valid": True,
            "critical_alerts": [],
            "warning_alerts": []
        }
        
        for sensor, value in data.items():
            if sensor in ["device_id", "sensor_id", "timestamp", "status"]:
                continue
                
            if sensor in self.critical_thresholds:
                thresholds = self.critical_thresholds[sensor]
                if thresholds["min"] > value or value > thresholds["max"]:
                    validation_results["valid"] = False
                    validation_results["critical_alerts"].append(
                        f"{sensor} critical: {value} (threshold: {thresholds['min']}-{thresholds['max']})"
                    )
            
            if sensor in self.warning_thresholds:
                thresholds = self.warning_thresholds[sensor]
                if thresholds["min"] > value or value > thresholds["max"]:
                    validation_results["warning_alerts"].append(
                        f"{sensor} warning: {value} (threshold: {thresholds['min']}-{thresholds['max']})"
                    )
        
        return validation_results

# ============ MQTT Callback functions with correct signatures ============

# For VERSION2 callback API
def on_connect_v2(client, userdata, flags, reason_code, properties=None):
    """Callback when connected to broker (VERSION2)"""
    if reason_code == 0:
        print(" Connected to MQTT broker successfully")
    else:
        print(f" Failed to connect to MQTT broker with code: {reason_code}")

def on_publish_v2(client, userdata, mid, reason_code, properties=None):
    """Callback when message is published (VERSION2)"""
    if reason_code == 0:
        print(f" Message {mid} published successfully")
    else:
        print(f" Failed to publish message {mid}: {reason_code}")

def on_disconnect_v2(client, userdata, flags, reason_code, properties=None):
    """Callback when disconnected from broker (VERSION2)"""
    if reason_code == 0:
        print("Disconnected from MQTT broker")
    else:
        print(f"Unexpected disconnection with code: {reason_code}")

# For VERSION1 callback API (backward compatibility)
def on_connect_v1(client, userdata, flags, rc):
    """Callback when connected to broker (VERSION1)"""
    if rc == 0:
        print(" Connected to MQTT broker successfully")
    else:
        print(f" Failed to connect to MQTT broker with code: {rc}")

def on_publish_v1(client, userdata, mid):
    """Callback when message is published (VERSION1)"""
    print(f" Message {mid} published successfully")

def on_disconnect_v1(client, userdata, rc):
    """Callback when disconnected from broker (VERSION1)"""
    if rc == 0:
        print("Disconnected from MQTT broker")
    else:
        print(f"Unexpected disconnection with code: {rc}")

# ==========================================================

def publish_sensor_data(mqtt_client, topic, data):
    """Publish sensor data to MQTT topic"""
    try:
        payload = json.dumps(data)
        result = mqtt_client.publish(topic, payload, qos=1)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            return True
        else:
            print(f"Failed to publish message: {result.rc}")
            return False
    except Exception as e:
        print(f"Error publishing message: {e}")
        return False

def connect_to_aws_iot():
    """Connect to AWS IoT Core"""
    print("\n" + "=" * 60)
    print("Connecting to AWS IoT Core...")
    print("=" * 60)
    print(f"Endpoint: {AWS_IOT_ENDPOINT}")
    print(f"Port: {AWS_IOT_PORT}")
    print(f"Client ID: {CLIENT_ID}")
    print(f"Topic: {AWS_IOT_TOPIC}")
    
    # Check if certificate files exist
    import os
    certs_ok = True
    if not os.path.exists(ROOT_CA):
        print(f" Warning: Root CA file not found at {ROOT_CA}")
        certs_ok = False
    if not os.path.exists(CERTIFICATE):
        print(f" Warning: Certificate file not found at {CERTIFICATE}")
        certs_ok = False
    if not os.path.exists(PRIVATE_KEY):
        print(f" Warning: Private key file not found at {PRIVATE_KEY}")
        certs_ok = False
    
    if not certs_ok:
        print("Certificate files missing. Please check the paths.")
        return None
    
    try:
        # Create MQTT client with callback API version 2
        mqtt_client = mqtt.Client(
            client_id=CLIENT_ID,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )
        
        # Configure TLS/SSL for AWS IoT Core
        mqtt_client.tls_set(
            ca_certs=ROOT_CA,
            certfile=CERTIFICATE,
            keyfile=PRIVATE_KEY,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLSv1_2
        )
        
        # Assign callback functions (VERSION2 signatures)
        mqtt_client.on_connect = on_connect_v2
        mqtt_client.on_publish = on_publish_v2
        mqtt_client.on_disconnect = on_disconnect_v2
        
        # Connect to AWS IoT Core
        print("Connecting...")
        mqtt_client.connect(AWS_IOT_ENDPOINT, AWS_IOT_PORT, 60)
        mqtt_client.loop_start()
        
        # Wait a moment to see if connection succeeds
        time.sleep(2)
        print(" Connected to AWS IoT Core successfully!")
        return mqtt_client
        
    except Exception as e:
        print(f" Failed to connect to AWS IoT Core: {e}")
        import traceback
        traceback.print_exc()
        return None

def connect_to_public_broker():
    """Connect to public MQTT broker (for testing)"""
    print("\n" + "=" * 60)
    print("Connecting to public MQTT broker...")
    print("=" * 60)
    print(f"Broker: {PUBLIC_MQTT_BROKER}")
    print(f"Port: {PUBLIC_MQTT_PORT}")
    print(f"Client ID: {CLIENT_ID}")
    print(f"Topic: {AWS_IOT_TOPIC}")
    
    try:
        # Create MQTT client with callback API version 2
        mqtt_client = mqtt.Client(
            client_id=CLIENT_ID,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )
        
        # Assign callback functions (VERSION2 signatures)
        mqtt_client.on_connect = on_connect_v2
        mqtt_client.on_publish = on_publish_v2
        mqtt_client.on_disconnect = on_disconnect_v2
        
        # Connect to public broker
        print("Connecting...")
        mqtt_client.connect(PUBLIC_MQTT_BROKER, PUBLIC_MQTT_PORT, 60)
        mqtt_client.loop_start()
        
        # Wait a moment to see if connection succeeds
        time.sleep(2)
        print(" Connected to public MQTT broker successfully!")
        return mqtt_client
        
    except Exception as e:
        print(f" Failed to connect to public broker: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("=" * 60)
    print("Waste Processing Plant Sensor Simulator")
    print("=" * 60)
    print(f"AWS IoT Mode: {USE_AWS_IOT}")
    
    # Connect to MQTT broker (AWS IoT or public)
    mqtt_client = None
    if USE_AWS_IOT:
        mqtt_client = connect_to_aws_iot()
        if not mqtt_client:
            print("\n Falling back to public broker...")
            mqtt_client = connect_to_public_broker()
    else:
        mqtt_client = connect_to_public_broker()
    
    if not mqtt_client:
        print(" Failed to connect to any MQTT broker. Exiting...")
        return
    
    # Initialize simulator
    simulator = WasteSensorSimulator()
    
    print("\n" + "=" * 60)
    print("Sensor Simulator Configuration")
    print("=" * 60)
    print(f"Device ID: {simulator.device_id}")
    print(f"Sensor ID: {simulator.sensor_id}")
    print(f"MQTT Topic: {AWS_IOT_TOPIC}")
    print("=" * 60)
    print("Starting data publishing...")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    message_count = 0
    normal_count = 0
    warning_count = 0
    critical_count = 0
    
    try:
        while True:
            message_count += 1
            
            # Generate sensor data
            sensor_data = simulator.generate_sensor_data()
            
            # Validate data
            validation = simulator.validate_data(sensor_data)
            
            # Update status based on validation
            if validation["critical_alerts"]:
                sensor_data["status"] = "CRITICAL"
                critical_count += 1
            elif validation["warning_alerts"]:
                sensor_data["status"] = "WARNING"
                warning_count += 1
            else:
                normal_count += 1
            
            # Add validation results to data
            sensor_data["critical_alerts"] = validation["critical_alerts"]
            sensor_data["warning_alerts"] = validation["warning_alerts"]
            
            # Publish to MQTT
            success = publish_sensor_data(mqtt_client, AWS_IOT_TOPIC, sensor_data)
            
            if success:
                print(f"\n[Message #{message_count}]")
                print(f"Timestamp: {sensor_data['timestamp']}")
                print(f"Status: {sensor_data['status']}")
                print(f"pH: {sensor_data['ph']}")
                print(f"Air Quality: {sensor_data['air_quality']}")
                print(f"Temperature: {sensor_data['temperature']}C")
                print(f"Weight: {sensor_data['weight']}kg")
                print(f"Pressure: {sensor_data['pressure']}hPa")
                print(f"Gas: {sensor_data['gas']}ppm")
                
                if validation["warning_alerts"]:
                    print("\n Warning Alerts:")
                    for alert in validation["warning_alerts"]:
                        print(f"  - {alert}")
                
                if validation["critical_alerts"]:
                    print("\n🔴 Critical Alerts:")
                    for alert in validation["critical_alerts"]:
                        print(f"  - {alert}")
            
            # Print statistics every 10 messages
            if message_count % 10 == 0:
                total = normal_count + warning_count + critical_count
                print(f"\n[Statistics - Last {total} messages]")
                print(f"  Normal: {normal_count} ({normal_count/total*100:.1f}%)")
                print(f"  Warning: {warning_count} ({warning_count/total*100:.1f}%)")
                print(f"  Critical: {critical_count} ({critical_count/total*100:.1f}%)")
                print("-" * 40)
            
            # Wait 3 seconds before next reading
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print(f"Simulator stopped. Total messages sent: {message_count}")
        print(f"Final Statistics: Normal={normal_count}, Warning={warning_count}, Critical={critical_count}")
        print("=" * 60)
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("Disconnected from MQTT broker")

if __name__ == "__main__":
    main()