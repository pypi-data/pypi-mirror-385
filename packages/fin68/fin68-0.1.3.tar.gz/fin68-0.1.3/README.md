# 🐍 Fin68 Python SDK

> **Fin68** mang tới bộ **client Python hiệu năng cao** để truy cập **hệ sinh thái dữ liệu tài chính Việt Nam**.  
> Thư viện được thiết kế **an toàn**, **linh hoạt** và **tối ưu cho ba nền tảng:**  
> 🪟 Windows | 🐧 Linux | 🍎 macOS

---

## 🚀 Cài đặt

Cài đặt trực tiếp từ [PyPI](https://pypi.org/project/fin68/):

```bash
pip install fin68
```

Yêu cầu:

- Python ≥ 3.9  
- pandas ≥ 2.1.2  
- requests

📘 [Tài liệu hướng dẫn](https://fin68.vn/docs/fin68py/)

---

## ⚙️ Khởi tạo nhanh

Ví dụ cơ bản để lấy dữ liệu giá đóng cửa của cổ phiếu **HPG** | chỉ số **VNINDEX** | ngành **Ngân hàng** trong năm 2023:

```python
import fin68 as fn

client = fn.client(apiKey="YOUR_API_KEY")
# Dữ liệu cổ phiếu
Stock = client.eod.stock
data = Stock.ohlcv(symbol="HPG", start="2023-01-01", end="2023-12-31")

# Dữ liệu chỉ số index
Market = client.eod.market
data = Market.ohlcv(symbol="VNINDEX", start="2023-01-01", end="2023-12-31")

# Dữ liệu ngành
Sector = client.eod.sector
data = Sector.ohlcv(symbol="Ngân hàng", start="2023-01-01", end="2023-12-31")
print(data)
```

📘 **Kết quả trả về** là `pandas.DataFrame` gồm các cột: `Date`, `Open`, `High`, `Low`, `Close`, `Volume`.

---

## 🧩 Cấu trúc thư viện

Fin68 được chia thành nhiều **client module** riêng biệt, mỗi module phụ trách một mảng dữ liệu:

| Module | Mô tả | Ví dụ truy cập |
|:--------|:------|:---------------|
| `client.eod` | Dữ liệu cuối ngày (EOD) | `client.eod.stock.ohlcv(symbol="HPG")` |
| `client.info` | Thông tin doanh nghiệp & cổ phiếu | `client.info.overview("VNM")` |
| `client.financials` | Báo cáo tài chính | `client.financials.statement("HPG")` |


Tất cả đều trả về **DataFrame** hoặc **dict** để dễ dàng xử lý trong phân tích định lượng.

---

## 🔐 Bảo mật & hiệu năng

- Tự động xác thực bằng `apiKey`  
- Kết nối HTTP được tối ưu hóa với `requests.Session`  
- Tuân thủ chuẩn [PEP 561](https://peps.python.org/pep-0561/) – hỗ trợ gợi ý kiểu (type hints)

---

## 📚 Bắt đầu khám phá

👉 Tiếp tục đọc tại:

- [**Tổng quan API**](api/index.md)  
- [**Clients: EOD, Info, Financials, Index**](api/clients/base.md)  
- [**Các kiểu dữ liệu & validator**](api/types.md)

Hoặc tra cứu chi tiết từng hàm trong **sidebar bên trái**.

---

## 🧠 Giấy phép & Liên hệ

- **License:** MIT  
- **Tác giả:** Fin68 Development Team  
- **Website:** [https://fin68.vn](https://fin68.vn)  
- **Liên hệ hỗ trợ:** [support@fin68.vn](mailto:support@fin68.vn)

---

> 💡 _Fin68 – Nền tảng dữ liệu mở, giúp nhà đầu tư, doanh nghiệp và lập trình viên tiếp cận dữ liệu tài chính Việt Nam một cách nhanh chóng và hiệu quả._