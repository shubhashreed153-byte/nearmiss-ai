from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET = os.path.join(BASE, "dataset", "trajectories.csv")

def analyse(df, filename):
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    aliases = {
        "vehicle": "vehicle_id",
        "vehicleid": "vehicle_id",
        "id": "vehicle_id",
        "timestamp": "time",
        "frame": "time",
        "lane_id": "lane",
        "x": "position",
        "longitudinal_position": "position",
        "velocity": "speed",
        "speed_mps": "speed"
    }
    df = df.rename(columns=aliases)

    required = ["vehicle_id", "time", "lane", "position", "speed"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return {"error": "Missing required columns: " + ", ".join(missing)}, 400

    for c in ["time", "position", "speed"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna(subset=required).copy()
    if df.empty:
        return {"error": "No valid trajectory records found."}, 400

    events = []

    for (time, lane), group in df.groupby(["time", "lane"]):
        group = group.sort_values("position").reset_index(drop=True)

        for i in range(len(group) - 1):
            rear = group.iloc[i]
            front = group.iloc[i + 1]

            gap = float(front["position"] - rear["position"])
            closing = float(rear["speed"] - front["speed"])

            if gap <= 0 or closing <= 0:
                continue

            ttc = gap / closing

            if ttc <= 5:
                events.append({
                    "time": float(time),
                    "lane": str(lane),
                    "rear_vehicle": str(rear["vehicle_id"]),
                    "front_vehicle": str(front["vehicle_id"]),
                    "gap": round(gap, 2),
                    "closing_speed": round(closing, 2),
                    "ttc": round(ttc, 2),
                    "risk": "HIGH" if ttc <= 2 else "MODERATE"
                })

    events.sort(key=lambda x: x["ttc"])

    return {
        "filename": filename,
        "records": int(len(df)),
        "vehicles": int(df["vehicle_id"].nunique()),
        "total_events": len(events),
        "high": sum(e["risk"] == "HIGH" for e in events),
        "moderate": sum(e["risk"] == "MODERATE" for e in events),
        "average_ttc": round(sum(e["ttc"] for e in events) / len(events), 2) if events else None,
        "events": events
    }, 200


@app.route("/sample", methods=["GET"])
def sample():
    if not os.path.exists(DATASET):
        return jsonify({"error": "dataset/trajectories.csv was not found."}), 404

    try:
        df = pd.read_csv(DATASET)
        result, status = analyse(df, "trajectories.csv")
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/analyze", methods=["POST"])
def analyze_upload():
    if "file" not in request.files:
        return jsonify({"error": "Please select a CSV file."}), 400

    file = request.files["file"]
    if not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Please upload a CSV file."}), 400

    try:
        df = pd.read_csv(file)
        result, status = analyse(df, file.filename)
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)