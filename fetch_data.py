import json
import os
import requests

# 1. ดึงข้อมูลจาก API HII
url = "https://www.thaiwater.net/proxy/riskrainfall48h.php?file=https://api.hii.or.th/v2/4UQaYnf0Bx4fXPYyCdDRbqHyXH9Ixvd2nVUjaN1cLBY=/warning/flashflood-48h"
response = requests.get(url)
raw_data = response.json()

# 2. เตรียมโครงสร้าง GeoJSON
geojson = {"type": "FeatureCollection", "features": []}

# หมายเหตุ: โครงสร้าง HII มักจะเก็บข้อมูลไว้ใน key ชื่อ 'data' หรือคล้ายกัน
# สามารถปรับเปลี่ยนชื่อ key (เช่น item['lat'], item['lon']) ให้ตรงกับข้อมูลจริงที่ API ส่งออกมาครับ
for item in raw_data.get("data", []):
    try:
        # ดึงค่าพิกัด ตรวจสอบให้แน่ใจว่าเป็นตัวเลข (float)
        lon = float(item.get("longitude", 0) or item.get("lon", 0))
        lat = float(item.get("latitude", 0) or item.get("lat", 0))

        feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "station_code": item.get("station_code"),
                "station_name": item.get("station_name"),
                "risk_level": item.get("risk_level"),
                "rain_24h": item.get("rain_24h"),
                "rain_48h": item.get("rain_48h"),
            },
        }
        geojson["features"].append(feature)
    except Exception as e:
        print(f"ข้ามข้อมูลเนื่องจากเกิดข้อผิดพลาด: {e}")

# 3. บันทึกไฟล์ลงใน Repository
with open("flashflood.geojson", "w", encoding="utf-8") as f:
    json.dump(geojson, f, ensure_ascii=False, indent=4)

print("แปลงไฟล์ GeoJSON สำเร็จและบันทึกเรียบร้อยแล้ว")
