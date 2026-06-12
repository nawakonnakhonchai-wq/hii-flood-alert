import json
import os
import requests

def main():
    # URL API ที่คุณใช้งาน
    url = "https://www.thaiwater.net/proxy/riskrainfall48h.php?file=https://api.hii.or.th/v2/4UQaYnf0Bx4fXPYyCdDRbqHyXH9Ixvd2nVUjaN1cLBY=/warning/flashflood-48h"
    
    # เพิ่ม Headers เพื่อเลียนแบบการเปิดผ่านเบราว์เซอร์ ป้องกันการบล็อก
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print("กำลังดึงข้อมูลจาก API...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        raw_data = response.json()
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลจาก API: {e}")
        return

    # สร้างโครงสร้าง GeoJSON FeatureCollection
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    # ตรวจสอบว่ามีข้อมูลในคีย์ "area" หรือไม่
    area_list = raw_data.get("area", [])
    print(f"พบข้อมูลสถานีทั้งหมด: {len(area_list)} จุด")

    for item in area_list:
        try:
            # ดึงค่าพิกัด ตรวจสอบและแปลงเป็นทศนิยม
            lon = float(item.get("longitude", 0))
            lat = float(item.get("latitude", 0))
            
            # ข้ามพิกัดที่เป็น 0,0
            if lon == 0 and lat == 0:
                continue

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "station_code": item.get("oldcode", ""),
                    "station_name": item.get("name", ""),
                    "tambon": item.get("tambon", ""),
                    "amphoe": item.get("amphoe", ""),
                    "province": item.get("province", ""),
                    "sum_rainfall_48h": item.get("sum_rainfall_48h", 0),
                    "agency": item.get("agency", ""),
                    "latest_rainfall_datetime": item.get("latest_rainfall_datetime", "")
                }
            }
            geojson["features"].append(feature)
            
        except (ValueError, TypeError):
            continue # ข้ามแถวที่พิกัดไม่ถูกต้อง
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการแปลงข้อมูล: {e}")

    # บันทึกไฟล์ GeoJSON
    output_filename = "flashflood.geojson"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(geojson, f, ensure_ascii=False, indent=4)
        print(f"บันทึกไฟล์ {output_filename} สำเร็จ แปลงข้อมูลได้ทั้งสิ้น {len(geojson['features'])} จุด")
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการบันทึกไฟล์: {e}")

if __name__ == "__main__":
    main()
