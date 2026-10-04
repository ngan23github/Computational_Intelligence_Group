# Project_Group_Computational_Intelligence_26_27

# Giải bài toán định tuyến xe (CVRP) bằng thuật toán đàn kiến (ACO)

Đồ án này cài đặt và so sánh nhiều biến thể của thuật toán tối ưu đàn kiến (Ant Colony Optimization) để giải bài toán định tuyến xe có ràng buộc tải trọng (Capacitated Vehicle Routing Problem - CVRP). Toàn bộ code nằm trong một notebook duy nhất để tiện theo dõi và chỉnh sửa.

## 1. Giới thiệu

### Bài toán CVRP

Có một kho (depot) và một tập khách hàng, mỗi khách có một lượng hàng cần giao (demand). Đội xe xuất phát từ kho, mỗi xe có sức chứa tối đa `Q`. Cần tìm các tuyến đường sao cho:

- Mỗi khách hàng được phục vụ đúng một lần.
- Tổng demand trên mỗi tuyến không vượt quá sức chứa xe.
- Mỗi tuyến bắt đầu và kết thúc tại kho.
- Tổng quãng đường của tất cả các xe là nhỏ nhất.

### Thuật toán

Notebook gồm 3 phiên bản để so sánh:

| Phiên bản | Mô tả |
|---|---|
| ACO Cơ Bản | Ant System kết hợp elitist, không có local search |
| ACO Nâng Cao | Min-Max Ant System (MMAS) + local search trong từng tuyến (2-opt, Or-opt) |
| ACO Cải Tiến | MMAS đã chỉnh lại + local search giữa các tuyến (relocate, swap, 2-opt*) |

## 2. Cấu trúc thư mục

```
.
├── ACO_VRP_Comparison_improved.ipynb   # notebook chính
├── README.md
└── data/
    ├── A-n32-k5.vrp                    # dữ liệu bài toán (CVRPLIB)
    └── A-n32-k5.sol                    # lời giải tối ưu (không bắt buộc, chỉ để vẽ)
```

Các module trong notebook (theo thứ tự các mục):

1. Import thư viện
2. VRP Parser: đọc file `.vrp` và `.sol`
3. Local Search trong tuyến: 2-opt, Or-opt
4. Visualizer: vẽ tuyến đường, đường hội tụ, biểu đồ so sánh
5. ACO Core: lớp `ACO_VRP` (AS, Elitist, MMAS)
6. Local search liên tuyến và lớp `ACO_VRP_Improved`
7. Đọc dữ liệu và vẽ instance
8. Chạy ACO Cơ Bản
9. Chạy ACO Nâng Cao
10. Chạy ACO Cải Tiến
11. Tổng kết và so sánh

## 3. Cài đặt môi trường

Yêu cầu: Python 3.9 trở lên.

### Bước 1: Tạo môi trường ảo (khuyến nghị)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Bước 2: Cài thư viện

```bash
pip install -r requirements.txt
```

### Bước 3: Chuẩn bị dữ liệu

1. Tải instance từ [CVRPLIB](http://vrp.galgos.inf.puc-rio.br/index.php/en/) (bộ A của Augerat et al.), ví dụ `A-n32-k5.vrp` và `A-n32-k5.sol`.
2. Tạo thư mục `data/` cùng cấp với notebook và bỏ file vào đó.

Muốn chạy instance khác thì sửa hai biến ở mục 6:

```python
DATA_FILE = 'data/A-n32-k5.vrp'
SOL_FILE = 'data/A-n32-k5.sol'
```

File `.sol` không bắt buộc. Nếu thiếu, notebook chỉ bỏ qua việc vẽ lộ trình tối ưu.

## 4. Cách chạy

```bash
jupyter notebook ACO_VRP_Comparison_improved.ipynb
```

Sau đó chọn **Kernel → Restart & Run All**, hoặc chạy lần lượt từng cell từ trên xuống dưới (các cell phụ thuộc nhau nên cần chạy theo thứ tự).

### Tham số chính

| Tham số | Ý nghĩa | Giá trị dùng trong notebook |
|---|---|---|
| `n_ants` | Số kiến mỗi vòng lặp | 30 |
| `n_iterations` | Số vòng lặp | 100 |
| `alpha` | Trọng số của pheromone | 1.0 |
| `beta` | Trọng số của heuristic (1/khoảng cách) | 3.0 |
| `rho` | Tốc độ bay hơi pheromone | 0.1 (bản cũ), 0.2 (bản cải tiến) |
| `cand_size` | Kích thước candidate list | 12 |
| `gb_period` | Cứ bao nhiêu vòng thì dùng global-best để cập nhật | 5 |
| `restart_after` | Số vòng không cải thiện thì reset pheromone | 30 |
| `seed` | Hạt giống ngẫu nhiên (để tái lập kết quả) | 42 |

## 5. Kết quả dự kiến

Kết quả đo trên instance A-n32-k5 (31 khách hàng, sức chứa xe 100, BKS = 784), với `n_ants=30`, `n_iterations=100`:

| Phiên bản | Cost dự kiến | Gap so với BKS | Số xe | Thời gian chạy |
|---|---|---|---|---|
| ACO Cơ Bản | khoảng 840 - 851 | khoảng +7% đến +9% | 5 | khoảng 2s |
| ACO Nâng Cao | khoảng 817 - 823 | khoảng +4% | 5 | khoảng 3.5s |
| ACO Cải Tiến | khoảng 787 | khoảng +0.4% | 5 | khoảng 25s |

Khi chạy xong, notebook sẽ in và vẽ:

- Sơ đồ vị trí khách hàng và kho.
- Lộ trình tối ưu từ file `.sol` (nếu có).
- Lộ trình của từng phiên bản kèm tải trọng mỗi xe.
- Đường cong hội tụ của cả ba phiên bản.
- Biểu đồ cột so sánh cost cuối cùng và gap so với BKS.

## 6. Hướng phát triển

- Chạy thêm các instance lớn hơn (A-n60, A-n80, B-n..., X-n...) và lập bảng kết quả trung bình qua nhiều seed.
- Làm ablation study: tắt từng cải tiến để xem mỗi cải tiến đóng góp bao nhiêu.
- Tinh chỉnh tham số (`alpha`, `beta`, `rho`, `cand_size`) bằng grid search.
- Thêm các move local search mạnh hơn (Or-opt liên tuyến, cross-exchange).
- Tăng tốc bằng Numba hoặc chạy song song nhiều kiến.

## 7. Tài liệu tham khảo

- M. Dorigo, T. Stützle. *Ant Colony Optimization*. MIT Press, 2004.
- T. Stützle, H. Hoos. MAX-MIN Ant System. *Future Generation Computer Systems*, 16(8), 2000.
- CVRPLIB: http://vrp.galgos.inf.puc-rio.br/
- P. Augerat et al. Computational results with a branch and cut code for the capacitated vehicle routing problem, 1995 (bộ dữ liệu A).