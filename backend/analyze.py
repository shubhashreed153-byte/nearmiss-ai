import pandas as pd
import json

df = pd.read_csv("dataset/trajectories.csv")
events = []

for t, frame in df.groupby("time"):
    for lane, cars in frame.groupby("lane"):
        cars = cars.sort_values("position")

        for i in range(len(cars)-1):
            rear, front = cars.iloc[i], cars.iloc[i+1]
            gap = front.position - rear.position
            closing = rear.speed - front.speed

            ttc = gap / closing if closing > 0 else None

            if ttc is not None and 0 < ttc <= 5:
                events.append({
                    "time": int(t),
                    "rear_vehicle": rear.vehicle_id,
                    "front_vehicle": front.vehicle_id,
                    "lane": int(lane),
                    "gap": round(float(gap), 2),
                    "ttc": round(float(ttc), 2),
                    "risk": "HIGH" if ttc <= 2 else "MODERATE"
                })

with open("dataset/analysis.json", "w") as f:
    json.dump(events, f, indent=2)

print("Analysis complete!")
print("Potential conflict events:", len(events))