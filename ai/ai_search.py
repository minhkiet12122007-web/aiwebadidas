from googlesearch import search
import requests


def get_comprehensive_info(product_name):
    # Kịch bản 1: Tìm link sản phẩm (ưu tiên Adidas)
    # Kịch bản 2: Tìm bài review/đánh giá chất liệu
    queries = [
        f"adidas {product_name} official description technology",
        f"đánh giá chi tiết giày adidas {product_name}",
        f"adidas {product_name} price and features"
    ]

    data = {
        "links": [],
        "snippets": []  # Lưu các đoạn mô tả ngắn từ Google
    }

    try:
        for q in queries:
            # Lấy nâng cao để có thêm thông tin
            results = list(search(q, pause=1))[:3]
            for url in results:
                if url not in data["links"]:
                    data["links"].append(url)
        return data
    except:
        return data
