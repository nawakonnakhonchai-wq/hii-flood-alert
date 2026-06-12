import json
import os
import requests

def main():
    # 1. ดึงข้อมูลจาก API HII
    url = "https://www.thaiwater.net/proxy/riskrainfall48h.php?file=https://api.hii.or.th/v2/4UQaYnf0Bx4fXPYyCdDRbqHyXH9Ixvd2nVUjaN1cLBY=/warning/flashflood-48h"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        raw_data = response.json()
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลจาก API: {e}")
        return

    # 2. เตรียมโครงสร้าง GeoJSON
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    # 3. วนลูปดึงข้อมูลจากอาเรย์ 'area'
    # ข้อมูลชุดนี้ใช้ 'area' เป็นที่เก็บออบเจกต์สถานีเฝ้าระวัง
    area_list = raw_data.get("area", [])
    
    for item in area_list:
        try:
            # ดึงค่าพิกัด แปลงเป็นตัวเลขทศนิยม (float)
            lon = float(item.get("longitude", 0))
            lat = float(item.get("latitude", 0))
            
            # ข้ามพิกัด 0,0 ที่อาจเป็นข้อมูลขยะ
            if lon == 0 and lat == 0:
                continue

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "station_code": item.get("oldcode"),
                    "station_name": item.get("name"),
                    "tambon": item.get("tambon"),
                    "amphoe": item.get("amphoe"),
                    "province": item.get("province"),
                    "sum_rainfall_48h": item.get("sum_rainfall_48h"),
                    "agency": item.get("agency"),
                    "latest_rainfall_datetime": item.get("latest_rainfall_datetime")
                }
            }
            geojson["features"].append(feature)
            
        except (ValueError, TypeError) as ve:
            print(f"ข้ามสถานีเนื่องจากพิกัดไม่ถูกต้อง: {item.get('name')} - Error: {ve}")
        except Exception as e:
            print(f"เกิดข้อผิดพลาด: {e}")

    # 4. บันทึกไฟล์ GeoJSON ลงใน Repository
    output_filename = "flashflood.geojson"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(geojson, f, ensure_ascii=False, indent=4)
        print(f"บันทึกไฟล์ {output_filename} สำเร็จ มีจุดเฝ้าระวังทั้งหมด {len(geojson['features'])} จุด")
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการบันทึกไฟล์: {e}")

if __name__ == "__main__":
    main()
