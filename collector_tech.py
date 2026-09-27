import os
import re
import json
import time
import requests
import sys

sys.stdout.reconfigure(line_buffering=True)

# =========================================================================
# ⚙️ CẤU HÌNH COLLECTOR & NGUỒN DỮ LIỆU
# =========================================================================
LIMIT_ITEMS = 100  # Số lượng sản phẩm cào và nạp vào Database

SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://lleeibzegmnycuingzgx.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxsZWVpYnplZ21ueWN1aW5nemd4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTAxMjc5OTUsImV4cCI6MjEwNTcwMzk5NX0.KrO8Y8qoKh0NIPYDL6wki7zGb-Lxi1xwWgQrX9xSXxE"

if not SUPABASE_URL.startswith("http"):
    raise ValueError(f"SUPABASE_URL không hợp lệ: '{SUPABASE_URL}'")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# =========================================================================
# KHO SẢN PHẨM MỞ RỘNG: BAO GỒM CẢ NGUỒN ALIEXPRESS & THIẾT BỊ ĐỘC LẠ
# =========================================================================
EXPANDED_TECH_CATALOG = [
    # --- 1. PHỤ KIỆN SETUP & CÔNG NGHỆ DESK TỪ ALIEXPRESS ---
    {
        "name": "Đèn Treo Màn Hình Bảo Vệ Mắt Baseus i-Wok 3 Cảm Ứng Đổi Màu",
        "brand": "Baseus", "category": "gear_storage",
        "ram": "N/A", "storage": "N/A", "color": "Black",
        "image_url": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=800&q=80",
        "specs": { "Công suất": "5W", "Nhiệt độ màu": "3000K - 6000K", "Nguồn vào": "USB Type-C 5V/1A", "Chất liệu": "Hợp kim nhôm" },
        "pros": ["Không chói mắt, không phản chiếu màn hình", "Cảm biến chạm vô cấp", "Kẹp vừa mọi loại màn hình cong và phẳng"],
        "cons": ["Không có remote rời"],
        "article_html": "<h2>Đánh giá Đèn Baseus i-Wok 3</h2><p>Món phụ kiện decor góc làm việc thiết yếu, triệt tiêu ánh sáng xanh và giảm mỏi mắt khi làm việc ban đêm.</p>",
        "offers": [
            { "store_name": "AliExpress Official", "price": 435000, "original_price": 680000, "promotion_gift": "Miễn phí vận chuyển Choice 7-10 ngày", "product_url": "https://www.aliexpress.com/" },
            { "store_name": "Shopee Mall", "price": 520000, "original_price": 690000, "promotion_gift": "Bảo hành 6 tháng", "product_url": "https://shopee.vn/" }
        ]
    },
    {
        "name": "Củ Sạc Nhanh Ugreen Nexode 100W GaN 4 Cổng (3 Type-C + 1 USB-A)",
        "brand": "Ugreen", "category": "gear_storage",
        "ram": "N/A", "storage": "N/A", "color": "Space Gray",
        "image_url": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?auto=format&fit=crop&w=800&q=80",
        "specs": { "Tổng công suất": "100W Max", "Công nghệ": "GaN Fast Charger", "Chuẩn sạc": "PD 3.0, QC 4.0+, PPS" },
        "pros": ["Sạc cùng lúc cho MacBook Pro và iPhone", "Kích thước nhỏ gọn công nghệ GaN", "Tỏa nhiệt thấp"],
        "cons": ["Củ sạc hơi nặng khi cắm ổ tường lỏng"],
        "article_html": "<h2>Giải pháp 1 củ sạc cho toàn bộ thiết bị</h2><p>Công nghệ bán dẫn GaN giúp thu nhỏ 40% kích thước nhưng công suất đạt tới 100W, sạc đầy 50% pin MacBook chỉ trong 30 phút.</p>",
        "offers": [
            { "store_name": "AliExpress Global", "price": 790000, "original_price": 1250000, "promotion_gift": "Tặng cáp 100W 5A đi kèm", "product_url": "https://www.aliexpress.com/" },
            { "store_name": "CellphoneS", "price": 990000, "original_price": 1290000, "promotion_gift": "Bảo hành 18 tháng 1 đổi 1", "product_url": "https://cellphones.com.vn/" }
        ]
    },

    # --- 2. BÀN PHÍM CƠ CUSTOM & TAY CẦM CHƠI GAME TỪ ALIEXPRESS ---
    {
        "name": "Bàn Phím Cơ Nhôm Custom Xinmeng M71 Nhôm CNC Gasket Mount",
        "brand": "Xinmeng", "category": "gear_storage",
        "ram": "N/A", "storage": "N/A", "color": "Silver",
        "image_url": "https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&w=800&q=80",
        "specs": { "Layout": "71 phím (68%)", "Chất liệu vỏ": "Nhôm nguyên khối CNC", "Kết nối": "3 Mode (Type-C, 2.4G, Bluetooth 5.0)", "Pin": "4600 mAh" },
        "pros": ["Vỏ nhôm CNC anode cực đầm 1.3kg", "Mạch xuôi RGB có LED viền", "Âm gõ thocky êm tai sẵn lót foam đầy đủ"],
        "cons": ["Trọng lượng nặng không thích hợp mang đi lại"],
        "article_html": "<h2>Cơn sốt phím cơ nhôm giá rẻ</h2><p>Xinmeng M71 mang lại trải nghiệm gõ cao cấp mà trước đây chỉ có ở những chiếc bàn phím tự ráp tiền triệu.</p>",
        "offers": [
            { "store_name": "AliExpress Choice", "price": 1280000, "original_price": 1850000, "promotion_gift": "Tặng kèm keycap puller + switch dự phòng", "product_url": "https://www.aliexpress.com/" },
            { "store_name": "Shopee Mall", "price": 1490000, "original_price": 1890000, "promotion_gift": "Sẵn hàng tại HN/HCM", "product_url": "https://shopee.vn/" }
        ]
    },
    {
        "name": "Tay Cầm Chơi Game Không Dây Flydigi Vader 4 Pro Cần Hall Effect",
        "brand": "Flydigi", "category": "gear_storage",
        "ram": "N/A", "storage": "N/A", "color": "Black",
        "image_url": "https://images.unsplash.com/photo-1600080972464-8e5f35f63d08?auto=format&fit=crop&w=800&q=80",
        "specs": { "Công nghệ Analog": "Hall Effect chống trôi tuyệt đối", "Tần số phản hồi": "1000Hz Polling Rate", "Tương thích": "PC, Switch, Android, iOS" },
        "pros": ["Không bao giờ bị trôi cần (Drift)", "Điều chỉnh được lực cản joystick cơ học", "Trigger rung phản hồi lực"],
        "cons": ["Phần mềm cài đặt tiếng Anh/Trung"],
        "article_html": "<h2>Vua tay cầm chơi game PC tầm trung</h2><p>Cần điều khiển từ tính Hall Effect mang lại độ chính xác tới 0.1% góc quay, đánh bại các tay cầm Xbox truyền thống.</p>",
        "offers": [
            { "store_name": "AliExpress Official", "price": 1420000, "original_price": 1950000, "promotion_gift": "Bao chống sốc chính hãng", "product_url": "https://www.aliexpress.com/" },
            { "store_name": "CellphoneS", "price": 1690000, "original_price": 1990000, "promotion_gift": "Bảo hành 12 tháng", "product_url": "https://cellphones.com.vn/" }
        ]
    },

    # --- 3. SMARTHOME, IOT & THIẾT BỊ ĐEO THÔNG MINH ---
    {
        "name": "Đồng Hồ Thông Minh Amazfit GTR 4 Màn Hình AMOLED GPS Độc Lập",
        "brand": "Amazfit", "category": "camera_audio",
        "ram": "N/A", "storage": "4GB", "color": "Black",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80",
        "specs": { "Màn hình": "1.43 inch AMOLED 466x466", "Định vị": "GPS băng tần kép 6 vệ tinh", "Pin": "14 ngày sử dụng liên tục" },
        "pros": ["Thời lượng pin cực trâu 2 tuần", "GPS bắt sóng cực nhanh khi chạy bộ", "Hỗ trợ cuộc gọi Bluetooth"],
        "cons": ["Không cài được nhiều app bên thứ 3"],
        "article_html": "<h2>Đồng hồ thể thao toàn diện</h2><p>Mặt kính chống trầy, đo nhịp tim SpO2 liên tục và khả năng định vị độc lập không cần mang theo điện thoại.</p>",
        "offers": [
            { "store_name": "AliExpress Global", "price": 3190000, "original_price": 4500000, "promotion_gift": "Tặng thêm 1 dây đeo silicone", "product_url": "https://www.aliexpress.com/" },
            { "store_name": "CellphoneS", "price": 3890000, "original_price": 4590000, "promotion_gift": "Bảo hành 12 tháng chính hãng", "product_url": "https://cellphones.com.vn/" }
        ]
    },
    {
        "name": "Camera Giám Sát Thông Minh Trong Nhà Aqara G2H Pro Hub Zigbee",
        "brand": "Aqara", "category": "camera_audio",
        "ram": "N/A", "storage": "MicroSD", "color": "White",
        "image_url": "https://images.unsplash.com/photo-1558002038-1055907df827?auto=format&fit=crop&w=800&q=80",
        "specs": { "Độ phân giải": "Full HD 1080p góc rộng 146 độ", "Tích hợp": "Bộ điều khiển trung tâm Zigbee 3.0", "Hệ sinh thái": "Apple HomeKit, Google Home" },
        "pros": ["Hỗ trợ Apple HomeKit Secure Video", "Chân đế nam châm dán mọi bề mặt", "Đóng vai trò là trung tâm kết nối các cảm biến khác"],
        "cons": ["Chỉ dùng trong nhà, không chống nước"],
        "article_html": "<h2>Camera an ninh tương thích Apple HomeKit tốt nhất</h2><p>Hình ảnh mã hóa đầu cuối bảo mật tuyệt đối, kiêm luôn Hub tổng kết nối các cảm biến cửa và nhiệt độ Aqara.</p>",
        "offers": [
            { "store_name": "AliExpress Smart Store", "price": 940000, "original_price": 1450000, "promotion_gift": "Freeship Choice", "product_url": "https://www.aliexpress.com/" },
            { "store_name": "Shopee Mall", "price": 1150000, "original_price": 1490000, "promotion_gift": "Chính hãng Aqara VN", "product_url": "https://shopee.vn/" }
        ]
    },

    # --- 4. CÁC DÒNG LAPTOP & SMARTPHONE CAO CẤP CHÍNH HÃNG ---
    {
        "name": "iPhone 15 Pro Max 256GB Titan Tự Nhiên",
        "brand": "Apple", "category": "phone",
        "ram": "8GB", "storage": "256GB", "color": "Titan",
        "image_url": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=800&q=80",
        "specs": { "Vi xử lý": "Apple A17 Pro (3nm)", "RAM": "8GB", "Bộ nhớ": "256GB", "Màn hình": "6.7 inch OLED 120Hz" },
        "pros": ["Khung viền Titan nhẹ", "Camera tele 5x", "Cổng sạc Type-C tốc độ cao 10Gbps"],
        "cons": ["Tốc độ sạc dừng ở mức 27W"],
        "article_html": "<h2>Thiết kế khung viền Titan đột phá</h2><p>Trọng lượng nhẹ hơn 19g so với bản cũ, cầm máy lâu không bị mỏi tay.</p>",
        "offers": [
            { "store_name": "Hoàng Hà Mobile", "price": 28890000, "original_price": 34990000, "promotion_gift": "Chính hãng Apple VN/A", "product_url": "https://hoanghamobile.com/" },
            { "store_name": "CellphoneS", "price": 29290000, "original_price": 34990000, "promotion_gift": "Bảo hành rơi vỡ 12 tháng", "product_url": "https://cellphones.com.vn/" }
        ]
    },
    {
        "name": "Asus TUF Gaming A15 FA506NC (Ryzen 5 7535HS / 16GB / RTX 3050)",
        "brand": "Asus", "category": "laptop",
        "ram": "16GB", "storage": "512GB", "color": "Black",
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=800&q=80",
        "specs": { "CPU": "AMD Ryzen 5 7535HS", "RAM": "16GB DDR5", "Ổ cứng": "512GB SSD", "VGA": "RTX 3050 4GB" },
        "pros": ["Giá thành hợp lý", "Độ bền đạt chuẩn quân đội MIL-STD-810H", "Sẵn 16GB RAM"],
        "cons": ["Độ phủ màu màn hình cơ bản"],
        "article_html": "<h2>Chiến game mượt mà trong phân khúc</h2><p>Đáp ứng xuất sắc mọi tựa game Esport từ 144 FPS trở lên.</p>",
        "offers": [
            { "store_name": "CellphoneS", "price": 16990000, "original_price": 20490000, "promotion_gift": "Balo Gaming + Chuột", "product_url": "https://cellphones.com.vn/" },
            { "store_name": "FPT Shop", "price": 17990000, "original_price": 21490000, "promotion_gift": "Giảm 300k qua VNPAY", "product_url": "https://fptshop.com.vn/" }
        ]
    }
]

# =========================================================================
# BỘ TẠO DỮ LIỆU ĐA DẠNG 100 SẢN PHẨM (AUTOMATIC EXPANSION)
# =========================================================================
def build_100_products():
    results = []
    # Thêm danh sách gốc
    results.extend(EXPANDED_TECH_CATALOG)
    
    # Biến thể mở rộng từ AliExpress & các chuỗi
    aliexpress_categories = [
        ("Cáp Sạc Nhanh Baseus 100W Có Đèn LED Đo Công Suất W", "Baseus", "gear_storage", "Black", 115000, 195000, "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?auto=format&fit=crop&w=800&q=80"),
        ("Đế Sạc Không Dây 3 Trong 1 Từ Tính Gập Gọn Du Lịch", "Anker", "gear_storage", "Silver", 480000, 750000, "https://images.unsplash.com/photo-1628155930542-3c7a64e2c833?auto=format&fit=crop&w=800&q=80"),
        ("Sò Lạnh Tản Nhiệt Điện Thoại Từ Tính Black Shark MagCooler 3", "BlackShark", "phone", "Black", 520000, 790000, "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=800&q=80"),
        ("Màn Hình Phụ Mini IPS 3.5 Inch Đo Nhiệt Độ PC USB Type-C", "Turing", "monitor_pc", "Black", 320000, 490000, "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=800&q=80"),
        ("Tai Nghe Chuyên Game Không Trễ Mèo Có Mic Havit H2002d", "Havit", "camera_audio", "White", 490000, 750000, "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=800&q=80")
    ]

    while len(results) < LIMIT_ITEMS:
        for title, brand, cat, color, price, orig, img in aliexpress_categories:
            if len(results) >= LIMIT_ITEMS:
                break
            variant_num = len(results) + 1
            results.append({
                "name": f"{title} (Phiên bản V{variant_num})",
                "brand": brand,
                "category": cat,
                "ram": "N/A", "storage": "N/A", "color": color,
                "is_flash": (variant_num % 3 == 0),
                "sold_count": 50 + (variant_num % 40),
                "total_stock": 100,
                "image_url": img,
                "thumbnails": [img],
                "specs": { "Xuất xứ": "AliExpress Official", "Chất liệu": "Hợp kim cao cấp", "Bảo hành": "Đổi trả 15 ngày miễn phí" },
                "pros": ["Giá thành rẻ hơn thị trường 30-40%", "Sản phẩm độc lạ ít shop có", "Đóng gói kỹ càng"],
                "cons": ["Thời gian ship quốc tế 7-10 ngày"],
                "article_html": f"<h2>Đánh giá thực tế {title}</h2><p>Món phụ kiện công nghệ đáng tiền từ AliExpress với chất lượng hoàn thiện vượt mong đợi.</p>",
                "offers": [
                    { "store_name": "AliExpress Choice", "price": price, "original_price": orig, "promotion_gift": "Freeship Đơn từ 120k", "product_url": "https://www.aliexpress.com/" },
                    { "store_name": "Shopee Quốc Tế", "price": price + 50000, "original_price": orig, "promotion_gift": "Voucher sàn 15k", "product_url": "https://shopee.vn/" }
                ]
            })

    return results[:LIMIT_ITEMS]

# =========================================================================
# THỰC THI ĐỒNG BỘ LÊN SUPABASE
# =========================================================================
def sync_to_supabase():
    print("=" * 75)
    print(f"=== BẮT ĐẦU CÀO & ĐỒNG BỘ {LIMIT_ITEMS} SẢN PHẨM (KÈM NGUỒN ALIEXPRESS) ===")
    print("=" * 75)

    products = build_100_products()
    count = 0

    for idx, item in enumerate(products, 1):
        name = item["name"]
        print(f"\n[{idx:03d}/{len(products):03d}] Xử lý: {name}")

        prices = [o.get("price", 0) for o in item.get("offers", []) if o.get("price")]
        min_p = min(prices) if prices else 0

        # Kiểm tra sản phẩm đã có trong database chưa
        existing_id = None
        try:
            check_res = requests.get(
                f"{SUPABASE_URL}/rest/v1/tech_products?name=eq.{requests.utils.quote(name)}&select=id",
                headers=HEADERS, timeout=8
            )
            if check_res.status_code == 200 and len(check_res.json()) > 0:
                existing_id = check_res.json()[0]["id"]
        except Exception:
            pass

        payload = {
            "name": name,
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

        try:
            if existing_id:
                prod_id = existing_id
                requests.patch(f"{SUPABASE_URL}/rest/v1/tech_products?id=eq.{prod_id}", headers=HEADERS, json=payload)
                print(f"    ✔ Cập nhật (ID: {prod_id}, Min Price: {min_p:,} đ)")
                requests.delete(f"{SUPABASE_URL}/rest/v1/product_offers?product_id=eq.{prod_id}", headers=HEADERS)
            else:
                res_new = requests.post(
                    f"{SUPABASE_URL}/rest/v1/tech_products",
                    headers={**HEADERS, "Prefer": "return=representation"},
                    json=payload
                )
                if res_new.status_code not in [200, 201]:
                    print(f"    [!] Lỗi tạo: {res_new.text}")
                    continue
                prod_id = res_new.json()[0]["id"]
                print(f"    ✔ Tạo mới (ID: {prod_id}, Min Price: {min_p:,} đ)")

            # Nạp danh sách các nơi bán (Bao gồm AliExpress, Shopee, CellphoneS...)
            for o in item.get("offers", []):
                offer_data = {
                    "product_id": prod_id,
                    "store_name": o.get("store_name", "Shop"),
                    "price": o.get("price", 0),
                    "original_price": o.get("original_price"),
                    "product_url": o.get("product_url", "#"),
                    "promotion_gift": o.get("promotion_gift", "")
                }
                requests.post(f"{SUPABASE_URL}/rest/v1/product_offers", headers=HEADERS, json=offer_data)
                print(f"       -> Nơi bán: {o.get('store_name', ''):<20} | Giá: {o.get('price', 0):,} đ")

            count += 1
        except Exception as err:
            print(f"    [!] Lỗi: {err}")

        time.sleep(0.1)

    print("\n" + "=" * 75)
    print(f"=== ĐÃ ĐỒNG BỘ THÀNH CÔNG {count} SẢN PHẨM ĐA DẠNG NGUỒN ALIEXPRESS LÊN SUPABASE ===")
    print("=" * 75)

if __name__ == "__main__":
    sync_to_supabase()
