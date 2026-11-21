import csv, os

os.makedirs("dataset", exist_ok=True)

with open("dataset/trajectories.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["time","vehicle_id","lane","position","speed"])

    for t in range(100):
        w.writerow([t,"V1",1,10+2*t,2.0])
        w.writerow([t,"V2",1,45+0.5*t,0.5])
        w.writerow([t,"V3",2,20+1.5*t,1.5])
        w.writerow([t,"V4",2,80+1.0*t,1.0])

print("NearMiss trajectory dataset created!")