# Judge audit

Lệnh chạy:
```bash
cd src
python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 5
python -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5
```

| Tiêu chí | n | Confusion (`FAIL`=POS) | κ | Precision | Recall | Fail rate (obs → Rogan-Gladen) | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|---|---|
| `tone_ok` | 100 | TP=24, FP=4, FN=6, TN=66 | **0.757** | **0.857** | **0.800** | `0.280` → `0.300` | **PASS** | **Dùng** (chỉ cho giọng điệu) |
| `helpful` | 100 | TP=9, FP=0, FN=21, TN=70 | **0.375** | **1.000** | **0.300** | `0.090` → `0.300` | **FAIL** (κ < 0.6, R < 0.7) | **Loại** |

## Audit thủ công bất đồng (6 case đại diện)

| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú & hành động sửa rubric |
|---|---|---|---|---|---|
| 1 | `H-008` (`tone_ok`) | PASS | FAIL | Người đúng (FN) | *"Em đã hoàn tiền cho anh rồi nha, anh check giúp em."* — quá suồng sã. **Sửa rubric:** bắt buộc xưng `"LogiX"`/`"anh/chị"`, cấm `nha`, `nhé`, `check giúp`. |
| 2 | `H-029` (`tone_ok`) | PASS | FAIL | Người đúng (FN) | *"Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm."* — giọng đuổi khách. **Sửa rubric:** thêm negative few-shot phạt cụm chặn tương tác dù có `"Dạ"`. |
| 3 | `H-051` (`tone_ok`) | FAIL | PASS | Người đúng (FP) | *"Dạ, LogiX đã refund 90.000đ cho đơn O-202 ạ."* — CSKH cho phép từ `"refund"`. **Sửa rubric:** whitelist từ mượn được phép (`refund`, `voucher`, `order`). |
| 4 | `H-081` (`tone_ok`) | FAIL | PASS | Judge đúng (lỗi nhãn) | Người chấm đọc nhầm ticket dẫn tới sai nhãn. **Hành động:** sửa golden label và áp dụng double-annotation cho các ca biên. |
| 5 | `HL-015` (`helpful`) | PASS | FAIL | Người đúng (FN) | *"Dạ, LogiX đã hoàn 55.000đ cho đơn O-112 ạ."* (ledger ghi `40.000đ`). Judge chỉ đọc text nên mù trước sai tiền. **Hành động:** thay bằng code grader `ReplyLedgerMatch` (FM-08). |
| 6 | `HL-016` (`helpful`) | PASS | FAIL | Người đúng (FN) | Xin lỗi dài dòng nhưng báo sai tiền (`55.000đ` vs ledger `35.000đ`). Dính *politeness/verbosity bias*. **Hành động:** bỏ judge `helpful`, tách giọng điệu (`tone_ok`) khỏi tính đúng số tiền (code). |

## Kết luận
- **Loại `judge_helpful` khỏi CI gate:** Ma trận nhầm lẫn (`TP=9, FP=0, FN=21, TN=70`) cho thấy dù `Precision=1.0`, judge bỏ sót **21/30 lỗi thật** (`Recall=0.300`, `κ=0.375`), khiến tỉ lệ lỗi quan sát bị đánh giá thấp ảo (`0.090` thay vì thực tế `0.300` theo Rogan-Gladen). Trong 21 ca FN có **18/21 ca sai tiền so với ledger** và **3/21 ca sai xưng hô** — dùng làm gate sẽ để lọt 70% regression.
- **Rủi ro còn lại:** Hiệu chuẩn mới thực hiện trên CSV replay công khai (`n=100`); sau khi sửa rubric cho `tone_ok` cần kiểm định lại trên tập **held-out mới do người gắn nhãn độc lập**.
