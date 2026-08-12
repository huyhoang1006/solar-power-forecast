# Hướng dẫn deploy model dự báo công suất điện mặt trời

## 1. File model được xuất

Sau khi huấn luyện thành công, bấm **Xuất model đã training** để tải file `.joblib`.
File này là một gói Python gồm:

- `mo_hinh`: model scikit-learn đã huấn luyện;
- `nen_dem_mw`: công suất nền dùng cho ban đêm;
- `van_tay`: mã nhận diện dữ liệu, biến đầu vào và thuật toán;
- `sieu_du_lieu`: thuật toán, đúng thứ tự biến đầu vào, phạm vi và thời điểm training.

Không tự đổi thứ tự biến trong `sieu_du_lieu["bien_dau_vao"]`. Model mặc định không
dùng nhiệt độ tấm pin.

Nút **Xuất model hiện tại** tải model đang được hệ thống sử dụng cho thuật toán đang
chọn, không cần training lại. Nút sẽ bị khóa nếu thuật toán đó chưa có model.

## 2. Chuẩn bị môi trường

Nên dùng cùng phiên bản Python và scikit-learn với máy training:

```bash
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

python -m pip install joblib numpy pandas scikit-learn
```

`joblib` có thể thực thi mã khi nạp. Chỉ dùng model do hệ thống tin cậy xuất ra và
nên lưu checksum SHA-256 của file trong quy trình phát hành.

## 3. Nạp model và dự báo

Tạo file `predictor.py`:

```python
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

MODEL_PATH = Path("nha_may_gbm_khong_nhiet.joblib")
goi = joblib.load(MODEL_PATH)

model = goi["mo_hinh"]
metadata = goi["sieu_du_lieu"]
feature_names = metadata["bien_dau_vao"]


def predict_power(rows: list[dict]) -> list[float]:
    """Mỗi dict phải có đủ biến đầu vào và đúng đơn vị lúc training."""
    frame = pd.DataFrame(rows)
    missing = [name for name in feature_names if name not in frame.columns]
    if missing:
        raise ValueError(f"Thiếu biến đầu vào: {missing}")

    values = frame.loc[:, feature_names].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Đầu vào chứa NaN hoặc giá trị vô hạn")

    prediction = model.predict(values)
    return np.clip(prediction, 0, 40).astype(float).tolist()
```

Các biến thường gặp của model mặc định:

- `ghi_wm2`: bức xạ ngang toàn phần, W/m²;
- `sol_elev`: góc cao mặt trời, độ;
- `sol_ha`: góc giờ mặt trời, độ;
- `ghi_ngoai_kq`: bức xạ ngoài khí quyển trên mặt phẳng ngang, W/m².

Luôn đọc `feature_names` từ file model thay vì ghi cứng danh sách này.

## 4. Tạo API bằng FastAPI

Tạo file `serve.py`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from predictor import predict_power

app = FastAPI(title="Solar Power Model")


class PredictionRequest(BaseModel):
    rows: list[dict[str, float]]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(request: PredictionRequest):
    try:
        return {"power_mw": predict_power(request.rows)}
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
```

Cài và chạy dịch vụ:

```bash
python -m pip install fastapi "uvicorn[standard]"
uvicorn serve:app --host 0.0.0.0 --port 8000
```

## 5. Kiểm tra trước production

1. Ghi lại checksum SHA-256 và `van_tay` của model được duyệt.
2. Kiểm tra `/health` và chạy một bộ đầu vào mẫu đã biết kết quả.
3. Xác nhận đầu vào đúng đơn vị, múi giờ và thứ tự feature.
4. Không gửi `t_panel_c` nếu `bien_dau_vao` không chứa biến này.
5. Theo dõi dữ liệu thiếu, giá trị ngoài miền training và công suất bị chặn ở 0–40 MW.
6. Chỉ thay model bằng bản đã kiểm thử và giữ model cũ để rollback.

Model chuyển bức xạ và hình học mặt trời thành công suất. Khi dự báo tương lai, chất
lượng kết quả còn phụ thuộc trực tiếp vào chất lượng dự báo bức xạ đầu vào.
