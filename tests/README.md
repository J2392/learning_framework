# Testing Framework for Learning Framework

Bộ tests này giúp kiểm tra chi tiết các thành phần của dự án Learning Framework, tuân theo nguyên tắc "less is more" nhưng vẫn cung cấp các công cụ kiểm thử chi tiết để phát hiện và xử lý vấn đề hiệu quả.

## Cài đặt môi trường

```bash
cd learning_framework/tests
python run_tests.py --setup --install-deps
```

Lệnh này sẽ:
1. Tạo các thư mục cần thiết
2. Tạo file `.env` mẫu nếu chưa tồn tại
3. Cài đặt các dependencies cần thiết cho tests

## Cấu trúc tests

```
tests/
├── README.md              # Tài liệu hướng dẫn này
├── requirements.txt       # Dependencies cho tests
├── run_tests.py           # Script chạy tests
├── test_api_connection.py # Kiểm tra kết nối API
├── test_api_requests.py   # Kiểm tra chi tiết API requests 
├── test_environment.py    # Kiểm tra cấu hình môi trường
├── test_generators.py     # Kiểm tra các generators
├── test_performance.py    # Benchmark hiệu năng
└── ... (các tests khác)
```

## Các loại tests

1. **Environment Tests**: Kiểm tra cấu hình, biến môi trường và thư mục
2. **API Connection Tests**: Kiểm tra kết nối đến Perplexity API
3. **API Request Tests**: Kiểm tra chi tiết các requests và responses
4. **Generator Tests**: Kiểm tra các generator (sentiment, summary, etc.)
5. **Performance Tests**: Benchmark hiệu năng và sử dụng tài nguyên

## Chạy tests

### Chạy tất cả tests

```bash
python run_tests.py
```

### Chạy tests cụ thể theo pattern

```bash
python run_tests.py --pattern api  # Chạy tất cả tests có "api" trong tên
```

### Chạy một test đơn lẻ

```bash
python run_tests.py --single test_environment.TestEnvironment.test_api_key_exists
```

### Chạy tests với verbose output

```bash
python run_tests.py --verbose
```

### Dừng khi gặp lỗi đầu tiên

```bash
python run_tests.py --stop-on-fail
```

### Chạy tests với pytest

```bash
python run_tests.py --pytest
```

### Chạy tests với coverage report

```bash
python run_tests.py --coverage
```

### Tạo HTML coverage report

```bash
python run_tests.py --coverage --html-report
```

## Kết quả tests

- Logs chi tiết được lưu trong thư mục `logs/`
- Kết quả generators được lưu trong thư mục `test_results/`
- Kết quả benchmark được lưu trong thư mục `bench_results/`

## Làm việc với API keys

- Đặt `PERPLEXITY_API_KEY` trong file `.env` để tests sử dụng API thực
- Đặt `DEVELOPMENT_MODE=True` trong file `.env` để sử dụng mock API

## Tùy chỉnh cho benchmark tests

- Đặt `QUICK_TEST=True` trong file `.env` để bỏ qua các tests toàn diện tốn thời gian
- Tùy chỉnh test data trong mỗi test file để phù hợp với nhu cầu kiểm thử

## Xử lý lỗi phổ biến

1. **ImportError**: Chạy `python run_tests.py --install-deps` để cài đặt các dependencies cần thiết
2. **ApiKey Error**: Kiểm tra API key trong file `.env`
3. **Module not found**: Đảm bảo bạn đang chạy tests từ thư mục gốc của dự án

## Mở rộng bộ tests

Khi thêm tests mới, hãy tuân theo các quy tắc sau:
- Đặt tên file bắt đầu bằng `test_`
- Tách biệt các loại test vào các file riêng
- Sử dụng pattern TestCase class của unittest
- Ghi log chi tiết để dễ dàng debug
- Lưu kết quả tests vào các thư mục tương ứng

## Tạo mock API cho tests

Khi cần test mà không có API key thực, bạn có thể sử dụng mock API trong module `mocks.mock_api.py`. Đặt `DEVELOPMENT_MODE=True` trong file `.env` để tự động sử dụng mock API.

---

Happy testing! 