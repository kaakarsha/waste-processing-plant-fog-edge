from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import json
import threading
import time
import logging
import boto3
from decimal import Decimal

# Initialize Flask
application = Flask(__name__)
app = application

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
REFRESH_INTERVAL = 5  # seconds
MAX_DATA_POINTS = 1000
DYNAMODB_TABLE_NAME = 'x25105990-dynamodb-table'

# Initialize DynamoDB
try:
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    logger.info(f"Connected to DynamoDB table: {DYNAMODB_TABLE_NAME}")
except Exception as e:
    logger.error(f"Failed to connect to DynamoDB: {e}")
    table = None

# Data cache
cache = {
    "latest": {},
    "recent": [],
    "stats": {},
    "alerts": [],
    "devices": set(),
    "last_update": None
}

def decimal_to_float(obj):
    """Convert Decimal to float for JSON serialization"""
    if isinstance(obj, list):
        return [decimal_to_float(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

def fetch_from_dynamodb(limit=100):
    """Fetch sensor data from DynamoDB"""
    if not table:
        logger.error("DynamoDB table not available")
        return []
    
    try:
        # Scan the table to get latest records
        response = table.scan(Limit=limit)
        items = response.get("Items", [])
        
        # Sort by timestamp descending
        items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Convert Decimal to float
        items = decimal_to_float(items)
        
        logger.info(f"Fetched {len(items)} records from DynamoDB")
        return items
        
    except Exception as e:
        logger.error(f"Error fetching from DynamoDB: {e}")
        import traceback
        traceback.print_exc()
        return []

def update_data_cache():
    """Background thread to update data cache from DynamoDB"""
    global cache
    
    while True:
        try:
            logger.info("Updating cache from DynamoDB...")
            
            # Fetch data from DynamoDB
            db_data = fetch_from_dynamodb(limit=MAX_DATA_POINTS)
            
            if db_data:
                # Update cache
                cache["recent"] = db_data
                cache["latest"] = db_data[0] if db_data else {}
                cache["last_update"] = datetime.now().isoformat()
                
                # Extract unique devices
                devices = set()
                for record in db_data:
                    device_id = record.get("device_id")
                    if device_id:
                        devices.add(device_id)
                cache["devices"] = devices
                
                logger.info(f"Cache updated with {len(db_data)} records, {len(devices)} devices")
                
                # Update statistics
                update_statistics()
                
                # Update alerts
                update_alerts()
            else:
                logger.warning("No data found in DynamoDB")
                
        except Exception as e:
            logger.error(f"Error updating cache: {e}")
            import traceback
            traceback.print_exc()
        
        # Wait before next update
        time.sleep(REFRESH_INTERVAL)

def update_statistics():
    """Calculate statistics from sensor data"""
    data = cache["recent"]
    if not data:
        return
    
    sensors = ["ph", "air_quality", "temperature", "weight", "pressure", "gas"]
    stats = {}
    
    for sensor in sensors:
        values = [d.get(sensor, 0) for d in data if d.get(sensor) is not None]
        if values:
            stats[sensor] = {
                "current": values[0] if values else 0,
                "avg": round(sum(values) / len(values), 2) if values else 0,
                "min": min(values) if values else 0,
                "max": max(values) if values else 0,
                "count": len(values)
            }
        else:
            stats[sensor] = {
                "current": 0,
                "avg": 0,
                "min": 0,
                "max": 0,
                "count": 0
            }
    
    # Add status statistics
    statuses = [d.get("status", "UNKNOWN") for d in data]
    stats["status_counts"] = {
        "NORMAL": statuses.count("NORMAL"),
        "WARNING": statuses.count("WARNING"),
        "CRITICAL": statuses.count("CRITICAL"),
        "UNKNOWN": statuses.count("UNKNOWN")
    }
    
    stats["total_records"] = len(data)
    stats["timestamp"] = datetime.now().isoformat()
    
    cache["stats"] = stats

def update_alerts():
    """Extract alerts from recent data"""
    data = cache["recent"]
    if not data:
        return
    
    alerts = []
    for record in data[:50]:  # Last 50 records
        critical_alerts = record.get("critical_alerts", [])
        warning_alerts = record.get("warning_alerts", [])
        
        # Check if critical_alerts and warning_alerts are lists
        if not isinstance(critical_alerts, list):
            critical_alerts = []
        if not isinstance(warning_alerts, list):
            warning_alerts = []
        
        if critical_alerts or warning_alerts:
            alerts.append({
                "timestamp": record.get("timestamp"),
                "device_id": record.get("device_id", "Unknown"),
                "status": record.get("status", "UNKNOWN"),
                "critical_alerts": critical_alerts,
                "warning_alerts": warning_alerts,
                "sensor_readings": {
                    "ph": record.get("ph"),
                    "air_quality": record.get("air_quality"),
                    "temperature": record.get("temperature"),
                    "weight": record.get("weight"),
                    "pressure": record.get("pressure"),
                    "gas": record.get("gas")
                }
            })
    
    cache["alerts"] = alerts[:20]  # Keep latest 20 alerts

# Start background cache update thread
cache_thread = threading.Thread(target=update_data_cache, daemon=True)
cache_thread.start()

@app.route("/")
def index():
    """Main dashboard page"""
    return render_template("dashboard.html", refresh_interval=REFRESH_INTERVAL)

@app.route("/api/data")
def get_data():
    """Get sensor data with optional filters"""
    limit = request.args.get("limit", 100, type=int)
    device_id = request.args.get("device_id")
    
    data = cache["recent"]
    
    if device_id:
        data = [d for d in data if d.get("device_id") == device_id]
    
    return jsonify({
        "success": True,
        "data": data[:limit],
        "total_records": len(data),
        "timestamp": datetime.now().isoformat()
    })

@app.route("/api/latest")
def get_latest():
    """Get latest sensor reading"""
    latest = cache["latest"]
    if latest:
        return jsonify({
            "success": True,
            "data": latest,
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({
            "success": False,
            "data": {},
            "message": "No data available",
            "timestamp": datetime.now().isoformat()
        })

@app.route("/api/stats")
def get_stats():
    """Get statistical summary"""
    return jsonify({
        "success": True,
        "stats": cache["stats"],
        "timestamp": datetime.now().isoformat()
    })

@app.route("/api/alerts")
def get_alerts():
    """Get active alerts"""
    return jsonify({
        "success": True,
        "alerts": cache["alerts"],
        "total_alerts": len(cache["alerts"]),
        "timestamp": datetime.now().isoformat()
    })

@app.route("/api/devices")
def get_devices():
    """Get list of unique devices"""
    return jsonify({
        "success": True,
        "devices": list(cache["devices"]),
        "total": len(cache["devices"])
    })

@app.route("/api/status")
def get_status():
    """Get system status"""
    return jsonify({
        "success": True,
        "cache": {
            "total_records": len(cache["recent"]),
            "latest_timestamp": cache["latest"].get("timestamp") if cache["latest"] else None,
            "devices": list(cache["devices"]),
            "alerts_count": len(cache["alerts"]),
            "last_update": cache["last_update"]
        },
        "dynamodb": {
            "connected": table is not None,
            "table_name": DYNAMODB_TABLE_NAME
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route("/api/refresh")
def refresh_data():
    """Force refresh data from DynamoDB"""
    logger.info("Force refreshing data from DynamoDB")
    
    try:
        db_data = fetch_from_dynamodb(limit=MAX_DATA_POINTS)
        
        if db_data:
            cache["recent"] = db_data
            cache["latest"] = db_data[0] if db_data else {}
            cache["last_update"] = datetime.now().isoformat()
            
            # Extract unique devices
            devices = set()
            for record in db_data:
                device_id = record.get("device_id")
                if device_id:
                    devices.add(device_id)
            cache["devices"] = devices
            
            update_statistics()
            update_alerts()
            
            return jsonify({
                "success": True,
                "message": f"Refreshed {len(db_data)} records from DynamoDB",
                "records": len(db_data),
                "devices": list(devices),
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "message": "No data found in DynamoDB",
                "timestamp": datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error refreshing data: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })

@app.route("/api/test")
def test_dynamodb():
    """Test DynamoDB connection"""
    try:
        if not table:
            return jsonify({
                "success": False,
                "message": "DynamoDB table not initialized"
            })
        
        # Try to get one record
        response = table.scan(Limit=1)
        items = response.get("Items", [])
        
        return jsonify({
            "success": True,
            "message": f"DynamoDB connection successful. Found {len(items)} records.",
            "sample": items[0] if items else None,
            "table_name": DYNAMODB_TABLE_NAME
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        })

if __name__ == "__main__":
    print("=" * 60)
    print("Waste Processing Plant Monitoring Dashboard")
    print("=" * 60)
    print(f"DynamoDB Table: {DYNAMODB_TABLE_NAME}")
    print(f"Refresh Interval: {REFRESH_INTERVAL} seconds")
    print(f"Max Data Points: {MAX_DATA_POINTS}")
    print("=" * 60)
    print("Critical Thresholds:")
    print("  pH: 4.0 - 9.5")
    print("  Air Quality: 0 - 300")
    print("  Temperature: 0 - 70C")
    print("  Weight: 100 - 8000kg")
    print("  Pressure: 950 - 1050hPa")
    print("  Gas: 0 - 1000ppm")
    print("=" * 60)
    print("Dashboard URL: http://localhost:5000")
    print("=" * 60)
    print("\nAPI Endpoints:")
    print("  GET /api/latest - Get latest reading")
    print("  GET /api/stats - Get statistics")
    print("  GET /api/alerts - Get alerts")
    print("  GET /api/devices - Get devices list")
    print("  GET /api/status - Get system status")
    print("  GET /api/refresh - Force refresh from DynamoDB")
    print("  GET /api/test - Test DynamoDB connection")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)