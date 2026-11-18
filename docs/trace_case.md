# Trace case: từ trace tới quyết định sai đầu tiên

Lệnh tái hiện:
```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

## Case phân tích: `seeded_regression C-002@11`

| Trường | Nội dung |
|---|---|
| **Trial** | `seeded_regression C-002@11`, report `E-seeded_regression-20261118-a26f` (`src/reports/eval_seeded_regression.json`, eval set SHA `a26f085c2f8f`). |
| **Triệu chứng** | `TrialPass` fail (`status resolved != denied`), `DbFactKept` = `False` (`1 override event(s)`), `RefundAmountCorrect` = `False` (`ledger=20000 != label=0`). Đọc **ledger trước reply**: `refund_ledger` ghi `refund_vnd=20000`, `refund_count=1` (nhãn chuẩn: `0`, `denied`), còn event #6 `reply` thông báo `"Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."`. |
| **Bước sai đầu tiên** | **Event #3** `model_override`: `{"delay_days": 5}` — ghi đè `delay_days=2` của DB đơn `O-202` bằng con số `"5 ngày"` trong ticket. |
| **Vì sao là bước *đầu tiên*** | **Event #1** (`handoff`) đúng phạm vi `owner_order_only` và tập tool chỉ đọc. **Event #2** (`investigator`) tra DB chính xác (`O-202`, `status="delivered"`, `delay_days=2`, `shipping_fee_vnd=20000`). Lỗi chỉ bắt đầu ở **Event #3**, kéo theo Event #4 (`quote` tính sai `20.000đ` theo `SHIP-LATE-03`) và lệnh ghi nhầm `20.000đ` vào ledger. |
| **Failure mode** | `FM-03` (`ticket_trust` — tin ticket hơn DB, layer `model/prompt`) trong [docs/failure_taxonomy.md](failure_taxonomy.md). |
| **Đối chứng** | Trên `fixed C-002@11` (`E-fixed-20261118-a26f`): không có `model_override`. Ngay sau Event #2 (`investigator`, `delay_days=2`), Event #3 `quote` trả `{"amount_vnd": 0, "reason": "no_entitlement"}`, Event #4 `reply` từ chối, ledger ghi `refund_vnd=0`, `refund_count=0`, `status=denied` (`TrialPass = PASS`). |
| **Regression test** | `test_trace_case_c002_fm03_regression` trong [src/tests/test_lab9_trace_case.py](../src/tests/test_lab9_trace_case.py) (assert `DbFactKept` + `RefundAmountCorrect`). Đã chạy `python -m pytest -q -m student -o addopts= tests/test_lab9_trace_case.py`: xác nhận **fail** trên `seeded_regression` và **pass** trên `fixed`. |
| **Chưa chắc chắn** | Trace chỉ bắt được bước sai ở mức event khi agent có log `model_override`; nếu biến thể có lỗi ẩn (`quiet_override`) sửa `delay_days` mà không ghi event này thì `DbFactKept` sẽ bỏ lọt — do đó luôn phải giữ `RefundAmountCorrect` đọc trực tiếp từ ledger làm chốt chặn cuối. |
