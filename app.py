from flask import Flask, jsonify, render_template
from flask_cors import CORS
import threading
import time
import random
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ===============================
# CONFIG
# ===============================
USE_SERIAL = False     # Set True if USB connected
DATA_FILE = "data.json"

# ===============================
# FILE HANDLER
# ===============================
def save_to_json(entry):
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    data.append(entry)

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ===============================
# LIVE DEVICE STATE
# ===============================
devices = {
    "NODE_01": {
        "device_id": "NODE_01",
        "lat": 10.91759,
        "lon":  76.98824,
        "status": "SOS"
    },
   
}

# ===============================
# SERIAL READER
# ===============================
def read_serial():
    import serial
    ser = serial.Serial('COM5', 9600, timeout=1)

    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if line:
            parts = line.split(",")
            if len(parts) == 4:
                entry = {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "device_id": parts[0],
                    "lat": float(parts[1]),
                    "lon": float(parts[2]),
                    "status": parts[3]
                }

                devices[parts[0]] = entry
                save_to_json(entry)

# ===============================
# FAKE DATA MODE
# ===============================
def fake_data():
    while True:
        for d in devices.values():
            d["lat"] += random.uniform(-0.0002, 0.0002)
            d["lon"] += random.uniform(-0.0002, 0.0002)

            entry = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "device_id": d["device_id"],
                "lat": round(d["lat"], 6),
                "lon": round(d["lon"], 6),
                "status": d["status"]
            }

            save_to_json(entry)

        time.sleep(5)

# ===============================
# START THREAD
# ===============================
if USE_SERIAL:
    threading.Thread(target=read_serial, daemon=True).start()
else:
    threading.Thread(target=fake_data, daemon=True).start()

# ===============================
# ROUTES
# ===============================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/data")
def data():
    return jsonify(list(devices.values()))

@app.route("/history")
def history():
    if not os.path.exists(DATA_FILE):
        return jsonify([])
    with open(DATA_FILE, "r") as f:
        return jsonify(json.load(f))

@app.route("/clear/<int:index>", methods=["DELETE"])
def clear_one(index):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    if 0 <= index < len(data):
        data.pop(index)

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

    return jsonify({"status": "deleted"})

@app.route("/clear_all", methods=["DELETE"])
def clear_all():
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

    return jsonify({"status": "cleared"})

# ===============================
# RUN SERVER
# ===============================
if __name__ == "__main__":
    app.run(debug=False)
