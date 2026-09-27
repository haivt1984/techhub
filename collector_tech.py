import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(line_buffering=True)

# Lấy biến môi trường an toàn, fallback về URL/Key nếu rỗng
SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://lleeibzegmnycuingzgx.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxsZWVpYnplZ21ueWN1aW5nemd4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTAxMjc5OTUsImV4cCI6MjEwNTcwMzk5NX0.KrO8Y8qoKh0NIPYDL6wki7zGb-Lxi1xwWgQrX9xSXxE"

if not SUPABASE_URL.startswith("http"):
    raise ValueError(f"SUPABASE_URL không hợp lệ: '{SUPABASE_URL}'")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Danh mục thiết bị chuẩn hóa
TECH_TARGETS = [
    {
        "name": "iPhone 15 Pro Max 256GB Titan Tự Nhiên",
        "brand": "Apple",
        "category": "phone",
        "ram": "8GB",
        "storage": "256GB",
        "color": "Titan",
        "is_flash": True,
        "sold_count": 88,
        "total_stock": 100,
        "image_url": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=800&q=80",
        "thumbnails": [
            "https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=300&q=80",
            "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?auto=format&fit=crop&w=300&q=80"
        ],
        "specs": {
            "Màn hình": "6.7 inch Super Retina XDR OLED, 120Hz",
            "Vi xử lý": "Apple A17 Pro (3nm)",
            "RAM": "8GB",
            "Bộ nhớ trong": "256GB",
            "Camera": "48MP + 12MP (Zoom 5x) + 12MP",
            "Khung viền": "Titan cấp độ 5",
            "Trọng lượng": "221g"
        },
        "pros": ["Khung viền Titan nhẹ, ít bám vân tay", "Camera tele 5x sắc nét", "Cổng sạc Type-C tốc độ cao 10Gbps"],
        "cons": ["Tốc độ sạc nhanh vẫn dừng ở mức 27W", "Giá phân khúc cao cấp"],
        "article_html": """
            <h2>1. Thiết kế khung viền Titan: Bước chuyển mình lớn về công thái học</h2>
            <p>Trọng lượng máy giảm xuống 221 gram nhờ khung viền Titan cao cấp. Các mép bo cong nhẹ giúp trải nghiệm cầm nắm thoải mái trong thời gian dài.</p>
            <h2>2. Camera tiềm vọng zoom quang 5x</h2>
            <p>Cảm biến tele tiêu cự 120mm cho độ sắc nét vượt trội, tái tạo chiều sâu ấn tượng và không bị vỡ hạt như zoom số.</p>
        """,
        "offers": [
            { "store_name": "Hoàng Hà Mobile", "price": 28890000, "original_price": 34990000, "promotion_gift": "Chính hãng Apple VN/A", "product_url": "https://hoanghamobile.com/" },
            { "store_name": "CellphoneS", "price": 29290000, "original_price": 34990000, "promotion_gift": "Bảo hành rơi vỡ 12 tháng", "product_url": "https://cellphones.com.vn/" },
            { "store_name": "FPT Shop", "price": 29490000, "original_price": 34990000, "promotion_gift": "Giảm 500k mở thẻ tín dụng", "product_url": "https://fptshop.com.vn/" }
        ]
    },
    {
        "name": "Samsung Galaxy S24 Ultra 5G 12GB / 256GB Đen Titan",
        "brand": "Samsung",
        "category": "phone",
        "ram": "12GB",
        "storage": "256GB",
        "color": "Black",
        "is_flash": True,
        "sold_count": 35,
        "total_stock": 60,
        "image_url": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?auto=format&fit=crop&w=800&q=80",
        "thumbnails": ["https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?auto=format&fit=crop&w=300&q=80"],
        "specs": {
            "Màn hình": "6.8 inch Dynamic AMOLED 2X, 120Hz phẳng",
            "Vi xử lý": "Snapdragon 8 Gen 3 for Galaxy",
            "RAM": "12GB",
            "Bộ nhớ": "256GB UFS 4.0",
            "Camera": "200MP + 50MP + 12MP + 10MP",
            "Pin": "5000 mAh, sạc 45W"
        },
        "pros": ["Màn hình phủ kính Corning Gorilla Armor chống lóa đỉnh cao", "Bút S-Pen tiện lợi", "Tính năng Galaxy AI dịch trực tiếp"],
        "cons": ["Thân máy vuông vức, trọng lượng 232g khá nặng"],
        "article_html": """
            <h2>1. Màn hình phẳng chống lóa xuất sắc</h2>
            <p>Mặt kính Gorilla Armor triệt tiêu tới 75% ánh sáng phản chiếu, giúp nhìn rõ ngoài trời nắng gắt.</p>
        """,
        "offers": [
            { "store_name": "Shopee Mall", "price": 26190000, "original_price": 31990000, "promotion_gift": "Voucher giảm 2 triệu", "product_url": "https://shopee.vn/" },
            { "store_name": "CellphoneS", "price": 26990000, "original_price": 31990000, "promotion_gift": "Tặng củ sạc nhanh 45W", "product_url": "https://cellphones.com.vn/" }
        ]
    },
    {
        "name": "Asus TUF Gaming A15 FA506NC (Ryzen 5 7535HS / 16GB / RTX 3050)",
        "brand": "Asus",
        "category": "laptop",
        "ram": "16GB",
        "storage": "512GB",
        "color": "Black",
        "is_flash": True,
        "sold_count": 42,
        "total_stock": 50,
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=800&q=80",
        "thumbnails": ["https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=300&q=80"],
        "specs": {
            "CPU": "AMD Ryzen 5 7535HS (6 nhân 12 luồng)",
            "RAM": "16GB DDR5 4800MHz",
            "Ổ cứng": "512GB SSD NVMe",
            "Card đồ họa": "NVIDIA GeForce RTX 3050 4GB",
            "Màn hình": "15.6 inch FHD 144Hz IPS",
            "Trọng lượng": "2.30 kg"
        },
        "pros": ["Giá thành hợp lý cho cấu hình RTX 3050", "Độ bền đạt chuẩn quân đội MIL-STD-810H", "Sẵn 16GB RAM DDR5"],
        "cons": ["Độ phủ màu màn hình ở mức cơ bản", "Bộ sạc tương đối cồng kềnh"],
        "article_html": """
            <h2>1. Chiến game mượt mà trong phân khúc phổ thông</h2>
            <p>Sự kết hợp giữa CPU Ryzen 5 và card đồ họa RTX 3050 cân mượt các tựa game Esport như Valorant, CS2 và GTA V trên 144 FPS.</p>
        """,
        "offers": [
            { "store_name": "CellphoneS", "price": 16990000, "original_price": 20490000, "promotion_gift": "Balo Gaming + Chuột", "product_url": "https://cellphones.com.vn/" },
            { "store_name": "Phong Vũ", "price": 17490000, "original_price": 20990000, "promotion_gift": "Bảo hành 24 tháng chính hãng", "product_url": "https://phongvu.vn/" },
            { "store_name": "FPT Shop", "price": 17990000, "original_price": 21490000, "promotion_gift": "Giảm 300k qua VNPAY", "product_url": "https://fptshop.com.vn/" }
        ]
    },
    {
        "name": "Apple MacBook Air 13 inch M2 8GB / 256GB SSD Bạc Ánh Sao",
        "brand": "Apple",
        "category": "laptop",
        "ram": "8GB",
        "storage": "256GB",
        "color": "Silver",
        "is_flash": False,
        "sold_count": 10,
        "total_stock": 30,
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80",
        "thumbnails": ["https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=300&q=80"],
        "specs": {
            "CPU": "Apple M2 8-core",
            "RAM": "8GB Unified Memory",
            "Ổ cứng": "256GB SSD",
            "Màn hình": "13.6 inch Liquid Retina, 500 nits",
            "Trọng lượng": "1.24 kg"
        },
        "pros": ["Thiết kế nhôm nguyên khối siêu mỏng 11.3mm", "Vận hành hoàn toàn yên tĩnh không quạt", "Pin trâu 18 tiếng"],
        "cons": ["Bản 8GB RAM không thể nâng cấp sau khi mua"],
        "article_html": """
            <h2>1. Mỏng nhẹ, sang trọng và yên tĩnh tuyệt đối</h2>
            <p>MacBook Air M2 mang lại trải nghiệm tối ưu cho người làm việc văn phòng nhờ thiết kế không quạt tản nhiệt và thời lượng pin cả ngày.</p>
        """,
        "offers": [
            { "store_name": "CellphoneS", "price": 23490000, "original_price": 26490000, "promotion_gift": "Thu cũ trợ giá 1 triệu", "product_url": "https://cellphones.com.vn/" },
            { "store_name": "Thế Giới Di Động", "price": 24290000, "original_price": 26990000, "promotion_gift": "Bảo hành 1 đổi 1 30 ngày", "product_url": "https://www.thegioididong.com/" }
        ]
    }
]

def check_product_exists(name):
    try:
        url = f"{SUPABASE_URL}/rest/v1/tech_products?name=eq.{requests.utils.quote(name)}&select=id"
        res = requests.get(url, headers=HEADERS, timeout=8)
        if res.status_code == 200 and len(res.json()) > 0:
            return res.json()[0]["id"]
    except Exception:
        pass
    return None

def sync_collector():
    print("=== BẮT ĐẦU CÀO & ĐỒNG BỘ GIÁ ĐỒ CÔNG NGHỆ (COLLECTOR ONLINE) ===")
    total_synced = 0

    for item in TECH_TARGETS:
        prod_name = item["name"]
        print(f"\n[*] Đang xử lý: {prod_name}")

        # Lấy giá an toàn bằng .get('price', 0)
        prices = [o.get("price", 0) for o in item.get("offers", []) if o.get("price")]
        min_p = min(prices) if prices else 0

        existing_id = check_product_exists(prod_name)
        
        product_payload = {
            "name": prod_name,
            "brand": item["brand"],
            "category": item["category"],
            "image_url": item["image_url"],
            "thumbnails": item.get("thumbnails", []),
            "is_flash": item.get("is_flash", False),
            "sold_count": item.get("sold_count", 0),
            "total_stock": item.get("total_stock", 100),
            "ram": item.get("ram", "N/A"),
            "storage": item.get("storage", "N/A"),
            "color": item.get("color", "Black"),
            "specs": item.get("specs", {}),
            "pros": item.get("pros", []),
            "cons": item.get("cons", []),
            "article_html": item.get("article_html", ""),
            "min_price": min_p
        }

        if existing_id:
            prod_id = existing_id
            requests.patch(f"{SUPABASE_URL}/rest/v1/tech_products?id=eq.{prod_id}", headers=HEADERS, json=product_payload)
            print(f"    ✔ Cập nhật sản phẩm (ID: {prod_id}, Min Price: {min_p:,} đ)")
            requests.delete(f"{SUPABASE_URL}/rest/v1/product_offers?product_id=eq.{prod_id}", headers=HEADERS)
        else:
            res_new = requests.post(
                f"{SUPABASE_URL}/rest/v1/tech_products",
                headers={**HEADERS, "Prefer": "return=representation"},
                json=product_payload
            )
            if res_new.status_code not in [200, 201]:
                print(f"    [!] Lỗi tạo sản phẩm: {res_new.text}")
                continue
            prod_id = res_new.json()[0]["id"]
            print(f"    ✔ Tạo mới sản phẩm (ID: {prod_id}, Min Price: {min_p:,} đ)")

        # Cập nhật danh sách nơi bán
        for offer in item.get("offers", []):
            offer_payload = {
                "product_id": prod_id,
                "store_name": offer.get("store_name", "Shop"),
                "price": offer.get("price", 0),
                "original_price": offer.get("original_price"),
                "product_url": offer.get("product_url", "#"),
                "promotion_gift": offer.get("promotion_gift", "")
            }
            requests.post(f"{SUPABASE_URL}/rest/v1/product_offers", headers=HEADERS, json=offer_payload)
            print(f"       -> Shop: {offer.get('store_name', ''):<18} | Giá: {offer.get('price', 0):,} đ")

        total_synced += 1
        time.sleep(0.5)

    print(f"\n=== HOÀN TẤT! ĐÃ ĐỒNG BỘ THÀNH CÔNG {total_synced} SẢN PHẨM VÀO SUPABASE ===")

if __name__ == "__main__":
    sync_collector()
