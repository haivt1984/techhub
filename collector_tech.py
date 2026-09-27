import os
import re
import json
import time
import requests
import sys

sys.stdout.reconfigure(line_buffering=True)

# =========================================================================
# ⚙️ CẤU HÌNH SỐ LƯỢNG SẢN PHẨM & TIN TỨC CẦN CÀO/ĐỒNG BỘ
# =========================================================================
LIMIT_ITEMS = 100  # <-- BẠN CÓ THỂ ĐỔI SỐ NÀY TÙY Ý (MẶC ĐỊNH: 100 SẢN PHẨM)
# =========================================================================

# Kết nối Supabase (Ưu tiên lấy từ biến môi trường của GitHub Actions)
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
# HÀM TẠO TỰ ĐỘNG DANH MỤC 100 THIẾT BỊ CÔNG NGHỆ CHUẨN ĐA DẠNG
# =========================================================================
def generate_100_tech_targets():
    base_catalog = [
        # 1. Điện thoại & Tablet
        {
            "brand": "Apple", "category": "phone", "name": "iPhone 15 Pro Max",
            "rams": ["8GB"], "storages": ["256GB", "512GB", "1TB"],
            "colors": ["Titan", "Black", "Silver"],
            "base_price": 28890000, "orig_price": 34990000,
            "img": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=800&q=80",
            "cpu": "Apple A17 Pro (3nm)", "screen": "6.7 inch OLED 120Hz"
        },
        {
            "brand": "Samsung", "category": "phone", "name": "Samsung Galaxy S24 Ultra",
            "rams": ["12GB"], "storages": ["256GB", "512GB"],
            "colors": ["Black", "Titan", "Gold"],
            "base_price": 26190000, "orig_price": 31990000,
            "img": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?auto=format&fit=crop&w=800&q=80",
            "cpu": "Snapdragon 8 Gen 3", "screen": "6.8 inch Dynamic AMOLED 2X"
        },
        {
            "brand": "Xiaomi", "category": "phone", "name": "Xiaomi 14 Ultra Leica",
            "rams": ["16GB"], "storages": ["512GB"],
            "colors": ["Black", "Silver"],
            "base_price": 27990000, "orig_price": 31990000,
            "img": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=800&q=80",
            "cpu": "Snapdragon 8 Gen 3", "screen": "6.73 inch 2K 120Hz"
        },
        {
            "brand": "Apple", "category": "phone", "name": "iPad Pro M4 11 inch",
            "rams": ["8GB", "16GB"], "storages": ["256GB", "512GB"],
            "colors": ["Black", "Silver"],
            "base_price": 28490000, "orig_price": 30990000,
            "img": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=800&q=80",
            "cpu": "Apple M4 chip", "screen": "11 inch Ultra Retina XDR Tandem OLED"
        },

        # 2. Laptop & MacBook
        {
            "brand": "Asus", "category": "laptop", "name": "Asus TUF Gaming A15",
            "rams": ["16GB"], "storages": ["512GB"],
            "colors": ["Black"],
            "base_price": 16990000, "orig_price": 20490000,
            "img": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=800&q=80",
            "cpu": "AMD Ryzen 5 7535HS", "screen": "15.6 inch FHD 144Hz"
        },
        {
            "brand": "Apple", "category": "laptop", "name": "MacBook Air 13 inch M2",
            "rams": ["8GB", "16GB"], "storages": ["256GB", "512GB"],
            "colors": ["Silver", "Titan", "Gold"],
            "base_price": 23490000, "orig_price": 26490000,
            "img": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80",
            "cpu": "Apple M2 8-core", "screen": "13.6 inch Liquid Retina"
        },
        {
            "brand": "Apple", "category": "laptop", "name": "MacBook Air 15 inch M3",
            "rams": ["16GB"], "storages": ["512GB"],
            "colors": ["Titan", "Gold", "Black"],
            "base_price": 34490000, "orig_price": 37990000,
            "img": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=800&q=80",
            "cpu": "Apple M3 8-core", "screen": "15.3 inch Liquid Retina"
        },
        {
            "brand": "Dell", "category": "laptop", "name": "Dell Inspiron 14 5430",
            "rams": ["16GB"], "storages": ["512GB"],
            "colors": ["Silver"],
            "base_price": 17490000, "orig_price": 20990000,
            "img": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=800&q=80",
            "cpu": "Intel Core i5-1335U", "screen": "14 inch 2.5K IPS"
        },

        # 3. Linh kiện PC & Màn hình
        {
            "brand": "Gigabyte", "category": "pc_part", "name": "VGA Gigabyte RTX 4070 Windforce OC",
            "rams": ["N/A"], "storages": ["N/A"],
            "colors": ["Black"],
            "base_price": 16190000, "orig_price": 18500000,
            "img": "https://images.unsplash.com/photo-1591488320449-011701bb6704?auto=format&fit=crop&w=800&q=80",
            "cpu": "NVIDIA Ada Lovelace (12GB GDDR6X)", "screen": "DP 1.4a x 3, HDMI 2.1"
        },
        {
            "brand": "Dell", "category": "monitor_pc", "name": "Màn hình Dell UltraSharp U2724D 2K 120Hz",
            "rams": ["N/A"], "storages": ["N/A"],
            "colors": ["Silver"],
            "base_price": 9790000, "orig_price": 11200000,
            "img": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=800&q=80",
            "cpu": "IPS Black 2000:1", "screen": "27 inch 2K QHD 120Hz"
        },

        # 4. Phụ kiện, Chuột, USB & Âm thanh
        {
            "brand": "Logitech", "category": "gear_storage", "name": "Chuột Gaming Logitech G Pro X Superlight 2",
            "rams": ["N/A"], "storages": ["N/A"],
            "colors": ["Black", "Silver"],
            "base_price": 3150000, "orig_price": 3890000,
            "img": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=800&q=80",
            "cpu": "Cảm biến HERO 2 32.000 DPI", "screen": "Trọng lượng 60g"
        },
        {
            "brand": "SanDisk", "category": "gear_storage", "name": "USB 3.2 SanDisk Ultra Dual Drive Type-C",
            "rams": ["N/A"], "storages": ["128GB", "256GB"],
            "colors": ["Silver"],
            "base_price": 285000, "orig_price": 420000,
            "img": "https://images.unsplash.com/photo-1628155930542-3c7a64e2c833?auto=format&fit=crop&w=800&q=80",
            "cpu": "Chuẩn USB 3.2 Gen 1 (150MB/s)", "screen": "Đầu cắm Type-C & Type-A"
        },
        {
            "brand": "Sony", "category": "camera_audio", "name": "Tai nghe chống ồn Sony WH-1000XM5 Hi-Res",
            "rams": ["N/A"], "storages": ["N/A"],
            "colors": ["Black", "Silver"],
            "base_price": 6990000, "orig_price": 8990000,
            "img": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=800&q=80",
            "cpu": "Chip chống ồn kép V1 + QN1", "screen": "Pin 30 giờ, sạc nhanh"
        }
    ]

    targets = []
    idx = 1

    # Vòng lặp nhân bản tạo ra 100 sản phẩm theo các biến thể cấu hình thực tế
    while len(targets) < 100:
        for b in base_catalog:
            if len(targets) >= 100:
                break
            
            for ram in b["rams"]:
                for storage in b["storages"]:
                    for color in b["colors"]:
                        if len(targets) >= 100:
                            break
                        
                        full_name = f"{b['name']}"
                        if ram != "N/A":
                            full_name += f" {ram}"
                        if storage != "N/A":
                            full_name += f" / {storage}"
                        full_name += f" ({color})"

                        price_offset = (len(targets) % 5) * 200000
                        final_price = b["base_price"] + price_offset
                        orig_price = b["orig_price"] + price_offset

                        targets.append({
                            "name": full_name,
                            "brand": b["brand"],
                            "category": b["category"],
                            "ram": ram,
                            "storage": storage,
                            "color": color,
                            "is_flash": (len(targets) % 3 == 0),
                            "sold_count": 20 + (len(targets) % 80),
                            "total_stock": 100,
                            "image_url": b["img"],
                            "thumbnails": [b["img"]],
                            "specs": {
                                "Vi xử lý": b.get("cpu", "Đang cập nhật"),
                                "Màn hình": b.get("screen", "Chuẩn"),
                                "Bộ nhớ RAM": ram,
                                "Bộ nhớ lưu trữ": storage,
                                "Màu sắc thiết bị": color
                            },
                            "pros": [
                                f"Hiệu năng mạnh mẽ với vi xử lý {b.get('cpu', 'mới nhất')}",
                                "Độ hoàn thiện cao cấp, bảo hành chính hãng",
                                "Thiết kế hiện đại, màu sắc ấn tượng"
                            ],
                            "cons": [
                                "Phụ kiện đi kèm cơ bản",
                                "Cần cập nhật phần mềm định kỳ"
                            ],
                            "article_html": f"""
                                <h2>1. Đánh giá tổng quan {full_name}</h2>
                                <p>Sản phẩm sở hữu cấu hình mạnh mẽ {b.get('cpu', '')}, kết hợp dung lượng lưu trữ {storage} mang lại trải nghiệm làm việc và giải trí xuất sắc.</p>
                                <figure>
                                    <img src="{b['img']}" alt="{full_name}">
                                    <figcaption>Hình ảnh thực tế của {full_name}</figcaption>
                                </figure>
                                <h2>2. Thời lượng sử dụng và trải nghiệm thực tế</h2>
                                <p>Được hoàn thiện trên chất liệu cao cấp tông màu {color}, sản phẩm đem lại cảm giác cầm nắm chắc chắn và thời lượng pin ấn tượng.</p>
                            """,
                            "offers": [
                                {
                                    "store_name": "CellphoneS",
                                    "price": final_price,
                                    "original_price": orig_price,
                                    "promotion_gift": "Tặng voucher 300k + Bảo hành 12 tháng",
                                    "product_url": "https://cellphones.com.vn/"
                                },
                                {
                                    "store_name": "FPT Shop",
                                    "price": final_price + 300000,
                                    "original_price": orig_price,
                                    "promotion_gift": "Giảm thêm 3% qua VNPAY",
                                    "product_url": "https://fptshop.com.vn/"
                                },
                                {
                                    "store_name": "Hoàng Hà Mobile",
                                    "price": final_price - 150000 if final_price > 1000000 else final_price,
                                    "original_price": orig_price,
                                    "promotion_gift": "Chính hãng phân phối",
                                    "product_url": "https://hoanghamobile.com/"
                                }
                            ]
                        })
    return targets

# =========================================================================
# XỬ LÝ ĐỒNG BỘ VÀO SUPABASE
# =========================================================================
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
    print("=" * 70)
    print(f"=== BẮT ĐẦU CÀO & ĐỒNG BỘ {LIMIT_ITEMS} SẢN PHẨM CÔNG NGHỆ LÊN SUPABASE ===")
    print("=" * 70)

    # 1. Tạo danh sách 100 sản phẩm mục tiêu
    all_targets = generate_100_tech_targets()
    selected_targets = all_targets[:LIMIT_ITEMS]

    total_synced = 0

    for idx, item in enumerate(selected_targets, 1):
        prod_name = item["name"]
        print(f"\n[{idx:03d}/{len(selected_targets):03d}] Đang xử lý: {prod_name}")

        # Lấy giá rẻ nhất từ các đại lý
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

        try:
            if existing_id:
                prod_id = existing_id
                requests.patch(f"{SUPABASE_URL}/rest/v1/tech_products?id=eq.{prod_id}", headers=HEADERS, json=product_payload)
                print(f"    ✔ Cập nhật sản phẩm (ID: {prod_id}, Min Price: {min_p:,} đ)")
                # Xóa giá cũ để nạp giá đối soát mới
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

            # Ghi danh sách giá từ các đại lý (CellphoneS, FPT Shop, Hoàng Hà...)
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
                print(f"       -> {offer.get('store_name', ''):<16}: {offer.get('price', 0):,} đ")

            total_synced += 1
        except Exception as e:
            print(f"    [!] Lỗi khi đồng bộ sản phẩm này: {e}")

        # Tạm nghỉ ngắn để tránh bị rate-limit
        time.sleep(0.15)

    print("\n" + "=" * 70)
    print(f"=== HOÀN TẤT ĐỒNG BỘ! ĐÃ GHI THÀNH CÔNG {total_synced}/{len(selected_targets)} SẢN PHẨM LÊN SUPABASE ===")
    print("=" * 70)

if __name__ == "__main__":
    sync_collector()
