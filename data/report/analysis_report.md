# Bao cao phan tich dataset

- Nguon: `/sessions/ecstatic-fervent-einstein/mnt/PythonProject8/db_fujiwara.sql`
- Database: **MEAS** (PostgreSQL 16.3)
- Dump tao luc: 2026-07-17 09:28:22
- Mui gio dia phuong dung trong bao cao: UTC+7
- So bang phan tich: 17

## 1. Tong quan truc thoi gian

| Bang | Dong | Cot | Bat dau (UTC) | Ket thuc (UTC) | So ngay | Buoc mau (s) | % dung buoc | Do phu % | Trung ts | So gap >3x | Gap lon nhat (h) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| His_131 | 521103 | 20 | 2025-07-12 16:37:05.237000 | 2026-07-17 02:27:08.892000 | 369.41 | 60 | 99.46 | 97.96 | 0 | 70 | 70.41 |
| His_431 | 524153 | 20 | 2025-07-12 04:54:58.786000 | 2026-07-17 02:27:08.934000 | 369.9 | 60 | 99.26 | 98.4 | 0 | 68 | 70.41 |
| His_431A | 250035 | 11 | 2025-07-05 09:49:41.372000 | 2026-07-17 02:27:08.971000 | 376.69 | 60 | 97.58 | 46.09 | 0 | 507 | 261.96 |
| His_432 | 256833 | 11 | 2025-07-14 22:30:46.344000 | 2026-07-17 02:27:08.986000 | 367.16 | 60 | 97.66 | 48.58 | 0 | 477 | 261.96 |
| His_433 | 247714 | 11 | 2025-07-09 23:38:34.717000 | 2026-07-17 02:27:09.007000 | 372.12 | 60 | 97.53 | 46.23 | 0 | 508 | 261.96 |
| His_434 | 251480 | 11 | 2025-07-09 05:48:46.881000 | 2026-07-17 02:27:09.035000 | 372.86 | 60 | 97.3 | 46.84 | 0 | 533 | 261.96 |
| His_435 | 250906 | 11 | 2025-07-10 22:28:48.112000 | 2026-07-17 02:27:09.050000 | 371.17 | 60 | 96.77 | 46.94 | 0 | 884 | 261.96 |
| His_436 | 256360 | 11 | 2025-07-06 00:59:08.803000 | 2026-07-17 02:27:09.097000 | 376.06 | 60 | 97.12 | 47.34 | 0 | 555 | 261.96 |
| His_437 | 252343 | 11 | 2025-07-16 06:58:05.162000 | 2026-07-17 02:27:09.111000 | 365.81 | 60 | 97.3 | 47.9 | 0 | 518 | 261.96 |
| His_471 | 519225 | 17 | 2025-07-05 17:35:04.417000 | 2026-07-17 02:27:09.132000 | 376.37 | 60 | 97.76 | 95.8 | 0 | 140 | 261.96 |
| His_473 | 519201 | 17 | 2025-07-05 18:53:05.071000 | 2026-07-17 02:27:09.169000 | 376.32 | 60 | 97.65 | 95.81 | 0 | 151 | 261.96 |
| His_475 | 519127 | 17 | 2025-07-05 18:45:05.038000 | 2026-07-17 02:27:09.191000 | 376.32 | 60 | 97.53 | 95.8 | 0 | 159 | 261.96 |
| His_477 | 519159 | 17 | 2025-07-05 19:56:05.719000 | 2026-07-17 02:27:09.242000 | 376.27 | 60 | 97.48 | 95.82 | 0 | 160 | 261.94 |
| His_T1 | 523932 | 11 | 2025-07-10 06:47:37.771000 | 2026-07-15 18:02:56.896000 | 370.47 | 60 | 97.66 | 98.21 | 0 | 146 | 71.37 |
| His_TUC41 | 521569 | 10 | 2025-07-06 07:03:59.620000 | 2026-07-15 20:49:57.783000 | 374.57 | 60 | 96.89 | 96.7 | 3 | 89 | 70.38 |
| His_report | 107307 | 71 | 2025-07-13 20:52:45.961000 | 2026-07-17 02:25:49.924000 | 368.23 | 300 | 96.75 | 101.18 | 0 | 10 | 70.47 |
| Weather | 524088 | 34 | 2025-07-12 14:58:42.835000 | 2026-07-17 02:27:09.279000 | 369.48 | 60 | 98.37 | 98.5 | 0 | 79 | 70.41 |

### Phan bo khoang cach giua cac mau

- **His_131**: 60s x518,303 (99.5%); 61s x1,810 (0.3%); 0s x205 (0.0%); 62s x128 (0.0%); 59s x61 (0.0%); 120s x44 (0.0%)
- **His_431**: 60s x520,273 (99.3%); 61s x1,949 (0.4%); 59s x547 (0.1%); 62s x281 (0.1%); 0s x169 (0.0%); 1s x127 (0.0%)
- **His_431A**: 60s x243,988 (97.6%); 61s x1,696 (0.7%); 59s x620 (0.2%); 62s x390 (0.2%); 58s x202 (0.1%); 63s x180 (0.1%)
- **His_432**: 60s x250,822 (97.7%); 61s x1,553 (0.6%); 59s x609 (0.2%); 62s x395 (0.2%); 58s x211 (0.1%); 63s x205 (0.1%)
- **His_433**: 60s x241,584 (97.5%); 61s x1,798 (0.7%); 59s x679 (0.3%); 62s x412 (0.2%); 58s x224 (0.1%); 63s x194 (0.1%)
- **His_434**: 60s x244,691 (97.3%); 61s x1,736 (0.7%); 59s x734 (0.3%); 62s x448 (0.2%); 63s x229 (0.1%); 58s x226 (0.1%)
- **His_435**: 60s x242,804 (96.8%); 61s x1,670 (0.7%); 59s x744 (0.3%); 62s x471 (0.2%); 58s x277 (0.1%); 63s x260 (0.1%)
- **His_436**: 60s x248,969 (97.1%); 61s x1,941 (0.8%); 59s x777 (0.3%); 62s x462 (0.2%); 58s x271 (0.1%); 63s x256 (0.1%)
- **His_437**: 60s x245,520 (97.3%); 61s x1,534 (0.6%); 59s x681 (0.3%); 62s x426 (0.2%); 58s x291 (0.1%); 63s x246 (0.1%)
- **His_471**: 60s x507,583 (97.8%); 61s x2,888 (0.6%); 59s x1,083 (0.2%); 62s x603 (0.1%); 92s x423 (0.1%); 63s x362 (0.1%)
- **His_473**: 60s x507,004 (97.7%); 61s x3,182 (0.6%); 59s x1,174 (0.2%); 62s x601 (0.1%); 92s x431 (0.1%); 63s x374 (0.1%)
- **His_475**: 60s x506,283 (97.5%); 61s x3,538 (0.7%); 59s x1,277 (0.2%); 62s x648 (0.1%); 92s x454 (0.1%); 58s x386 (0.1%)
- **His_477**: 60s x506,064 (97.5%); 61s x3,798 (0.7%); 59s x1,462 (0.3%); 62s x698 (0.1%); 92s x404 (0.1%); 58s x388 (0.1%)
- **His_T1**: 60s x511,658 (97.7%); 61s x4,007 (0.8%); 59s x1,625 (0.3%); 62s x771 (0.1%); 58s x404 (0.1%); 63s x315 (0.1%)
- **His_TUC41**: 60s x505,355 (96.9%); 61s x4,332 (0.8%); 59s x1,660 (0.3%); 62s x757 (0.1%); 58s x419 (0.1%); 63s x325 (0.1%)
- **His_report**: 300s x103,819 (96.8%); 0s x2,103 (2.0%); 301s x865 (0.8%); 1s x71 (0.1%); 299s x66 (0.1%); 302s x30 (0.0%)
- **Weather**: 60s x515,537 (98.4%); 61s x3,765 (0.7%); 59s x1,617 (0.3%); 62s x703 (0.1%); 58s x331 (0.1%); 63s x247 (0.0%)

## 2. Phan loai cot theo y nghia vat ly

| table      |   active_power |   current |   frequency |   humidity |   irradiance |   meta |   other |   performance_ratio |   power_factor |   pressure |   reactive_power |   tap_changer |   temperature |   time |   voltage |   wind |
|:-----------|---------------:|----------:|------------:|-----------:|-------------:|-------:|--------:|--------------------:|---------------:|-----------:|-----------------:|--------------:|--------------:|-------:|----------:|-------:|
| His_131    |              1 |         4 |           1 |          0 |            0 |      3 |       0 |                   0 |              1 |          0 |                1 |             0 |             0 |      3 |         6 |      0 |
| His_431    |              1 |         4 |           1 |          0 |            0 |      3 |       0 |                   0 |              1 |          0 |                1 |             0 |             0 |      3 |         6 |      0 |
| His_431A   |              1 |         4 |           0 |          0 |            0 |      3 |       0 |                   0 |              0 |          0 |                0 |             0 |             0 |      3 |         0 |      0 |
| His_432    |              1 |         4 |           0 |          0 |            0 |      3 |       0 |                   0 |              0 |          0 |                0 |             0 |             0 |      3 |         0 |      0 |
| His_433    |              1 |         4 |           0 |          0 |            0 |      3 |       0 |                   0 |              0 |          0 |                0 |             0 |             0 |      3 |         0 |      0 |
| His_434    |              1 |         4 |           0 |          0 |            0 |      3 |       0 |                   0 |              0 |          0 |                0 |             0 |             0 |      3 |         0 |      0 |
| His_435    |              1 |         4 |           0 |          0 |            0 |      3 |       0 |                   0 |              0 |          0 |                0 |             0 |             0 |      3 |         0 |      0 |
| His_436    |              1 |         4 |           0 |          0 |            0 |      3 |       0 |                   0 |              0 |          0 |                0 |             0 |             0 |      3 |         0 |      0 |
| His_437    |              1 |         4 |           0 |          0 |            0 |      3 |       0 |                   0 |              0 |          0 |                0 |             0 |             0 |      3 |         0 |      0 |
| His_471    |              1 |         4 |           1 |          0 |            0 |      3 |       0 |                   0 |              1 |          0 |                1 |             0 |             0 |      3 |         3 |      0 |
| His_473    |              1 |         4 |           1 |          0 |            0 |      3 |       0 |                   0 |              1 |          0 |                1 |             0 |             0 |      3 |         3 |      0 |
| His_475    |              1 |         4 |           1 |          0 |            0 |      3 |       0 |                   0 |              1 |          0 |                1 |             0 |             0 |      3 |         3 |      0 |
| His_477    |              1 |         4 |           1 |          0 |            0 |      3 |       0 |                   0 |              1 |          0 |                1 |             0 |             0 |      3 |         3 |      0 |
| His_T1     |              0 |         0 |           0 |          0 |            0 |      3 |       0 |                   0 |              0 |          0 |                0 |             1 |             4 |      3 |         0 |      0 |
| His_TUC41  |              0 |         0 |           1 |          0 |            0 |      3 |       0 |                   0 |              0 |          0 |                0 |             0 |             0 |      3 |         3 |      0 |
| His_report |              9 |        27 |           2 |          1 |            3 |      3 |       1 |                   1 |              2 |          1 |                6 |             1 |             7 |      3 |         2 |      2 |
| Weather    |              4 |         0 |           0 |          3 |            5 |      3 |       1 |                   0 |              0 |          3 |                0 |             0 |             6 |      3 |         0 |      6 |

## 3. Canh bao chat luong du lieu

- `His_131.Substation_Level_110kV_Bay131_MEAS_P` — 17.988% gia tri am (tieu thu tu luoi hoac sai dau).
- `His_431.Substation_Level_22kV_Bay431_MEAS_In` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `His_431.Substation_Level_22kV_Bay431_MEAS_In` — 100.0% gia tri bang 0, nghi ngo tag chet hoac NULL bi ghi thanh 0.
- `His_431A.Substation_Level_22kV_Bay431A_MEAS_P` — **gia tri dot bien**: max=4,410,466 trong khi p99=6.14 (gap 718,016 lan). Phai loc truoc khi huan luyen.
- `His_471.Substation_Level_22kV_Bay471_Meas_Uc` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `His_471.Substation_Level_22kV_Bay471_Meas_Uc` — thieu 100.0% du lieu.
- `His_471.Substation_Level_22kV_Bay471_Meas_Ub` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `His_471.Substation_Level_22kV_Bay471_Meas_Ub` — thieu 100.0% du lieu.
- `His_471.Substation_Level_22kV_Bay471_Meas_Ua` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `His_471.Substation_Level_22kV_Bay471_Meas_Ua` — thieu 100.0% du lieu.
- `His_473.Substation_Level_22kV_Bay473_Meas_In` — 98.855% gia tri bang 0, nghi ngo tag chet hoac NULL bi ghi thanh 0.
- `His_473.Substation_Level_22kV_Bay473_Meas_Uc` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `His_473.Substation_Level_22kV_Bay473_Meas_Uc` — thieu 100.0% du lieu.
- `His_473.Substation_Level_22kV_Bay473_Meas_Ub` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `His_473.Substation_Level_22kV_Bay473_Meas_Ub` — thieu 100.0% du lieu.
- `His_473.Substation_Level_22kV_Bay473_Meas_Ua` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `His_473.Substation_Level_22kV_Bay473_Meas_Ua` — thieu 100.0% du lieu.
- `His_475.Substation_Level_22kV_Bay475_Meas_Uc` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `His_475.Substation_Level_22kV_Bay475_Meas_Uc` — thieu 100.0% du lieu.
- `His_475.Substation_Level_22kV_Bay475_Meas_Ub` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `His_475.Substation_Level_22kV_Bay475_Meas_Ub` — thieu 100.0% du lieu.
- `His_475.Substation_Level_22kV_Bay475_Meas_Ua` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `His_475.Substation_Level_22kV_Bay475_Meas_Ua` — thieu 100.0% du lieu.
- `His_477.Substation_Level_22kV_Bay477_Meas_In` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `His_477.Substation_Level_22kV_Bay477_Meas_In` — 99.97% gia tri bang 0, nghi ngo tag chet hoac NULL bi ghi thanh 0.
- `His_477.Substation_Level_22kV_Bay477_Meas_Uc` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `His_477.Substation_Level_22kV_Bay477_Meas_Uc` — thieu 100.0% du lieu.
- `His_477.Substation_Level_22kV_Bay477_Meas_Ub` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `His_477.Substation_Level_22kV_Bay477_Meas_Ub` — thieu 100.0% du lieu.
- `His_477.Substation_Level_22kV_Bay477_Meas_Ua` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `His_477.Substation_Level_22kV_Bay477_Meas_Ua` — thieu 100.0% du lieu.
- `His_T1.Substation_Level_110kV_BayT1_T1_MEAS_Tap` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `His_T1.Substation_Level_110kV_BayT1_T1_MEAS_MVTemp` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `His_T1.Substation_Level_110kV_BayT1_T1_MEAS_MVTemp` — thieu 100.0% du lieu.
- `His_report.Data_PR` — **gia tri dot bien**: max=54,108 trong khi p99=122.03 (gap 443 lan). Phai loc truoc khi huan luyen.
- `His_report.IEC104S_IEC104S_AI_P_LOW` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `His_report.Substation_Level_110kV_BayT1_T1_MEAS_Tap` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `His_report.Substation_Level_110kV_BayT1_T1_MEAS_MVTemp` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `His_report.Substation_Level_110kV_BayT1_T1_MEAS_MVTemp` — thieu 100.0% du lieu.
- `His_report.Substation_Level_110kV_Bay131_MEAS_P` — 17.539% gia tri am (tieu thu tu luoi hoac sai dau).
- `His_report.SOLAR_WSRT1_Rad_1` — buc xa max = 1501.0 W/m2, vuot nguong vat ly (GHI cuc dai ~1200-1400 W/m2 ke ca cloud enhancement).
- `Weather.SOLAR_WS_Rad_2` — buc xa max = 1453.469 W/m2, vuot nguong vat ly (GHI cuc dai ~1200-1400 W/m2 ke ca cloud enhancement).
- `Weather.SOLAR_WS_Rad_1` — buc xa max = 1401.0 W/m2, vuot nguong vat ly (GHI cuc dai ~1200-1400 W/m2 ke ca cloud enhancement).
- `Weather.SOLAR_WS_Panel_T` — **gia tri dot bien**: max=6,554 trong khi p99=52.20 (gap 126 lan). Phai loc truoc khi huan luyen.
- `Weather.Data_WS2_Wind_Speed` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `Weather.Data_WS2_Wind_Speed` — thieu 100.0% du lieu.
- `Weather.Data_WS2_Wind_direction` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `Weather.Data_WS2_Wind_direction` — thieu 100.0% du lieu.
- `Weather.Data_WS2_Rad_2` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `Weather.Data_WS2_Rad_2` — thieu 100.0% du lieu.
- `Weather.Data_WS2_Panel_T` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `Weather.Data_WS2_Panel_T` — thieu 100.0% du lieu.
- `Weather.Data_WS2_Humidity` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `Weather.Data_WS2_Humidity` — thieu 100.0% du lieu.
- `Weather.Data_WS2_Air_T` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `Weather.Data_WS2_Air_T` — thieu 100.0% du lieu.
- `Weather.Data_WS2_Air_Pressure` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `Weather.Data_WS2_Air_Pressure` — thieu 100.0% du lieu.
- `Weather.Data_WS1_Wind_Speed` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `Weather.Data_WS1_Wind_Speed` — thieu 93.17% du lieu.
- `Weather.Data_WS1_Wind_direction` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `Weather.Data_WS1_Wind_direction` — thieu 93.17% du lieu.
- `Weather.Data_WS1_Rad_2` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `Weather.Data_WS1_Rad_2` — thieu 93.17% du lieu.
- `Weather.Data_WS1_Rad_1` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `Weather.Data_WS1_Rad_1` — thieu 93.17% du lieu.
- `Weather.Data_WS1_Panel_T` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `Weather.Data_WS1_Panel_T` — thieu 93.17% du lieu.
- `Weather.Data_WS1_Humidity` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `Weather.Data_WS1_Humidity` — thieu 93.17% du lieu.
- `Weather.Data_WS1_Air_T` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `Weather.Data_WS1_Air_T` — thieu 93.17% du lieu.
- `Weather.Data_WS1_Air_Pressure` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `Weather.Data_WS1_Air_Pressure` — thieu 100.0% du lieu.
- `Weather.IEC104S_IEC104S_AI_P_LOW` — **hang so** (chi 1 gia tri), khong dung lam feature.
- `His_131` — du lieu KHONG sap xep theo thoi gian trong file, phai sort truoc khi tinh chuoi thoi gian.
- `His_431` — du lieu KHONG sap xep theo thoi gian trong file, phai sort truoc khi tinh chuoi thoi gian.
- `His_431A` — do phu chi 46.09% (mat 4881.59 gio).
- `His_431A` — du lieu KHONG sap xep theo thoi gian trong file, phai sort truoc khi tinh chuoi thoi gian.
- `His_432` — do phu chi 48.58% (mat 4539.62 gio).
- `His_432` — du lieu KHONG sap xep theo thoi gian trong file, phai sort truoc khi tinh chuoi thoi gian.
- `His_433` — do phu chi 46.23% (mat 4809.82 gio).
- `His_433` — du lieu KHONG sap xep theo thoi gian trong file, phai sort truoc khi tinh chuoi thoi gian.
- `His_434` — do phu chi 46.84% (mat 4764.97 gio).
- `His_434` — du lieu KHONG sap xep theo thoi gian trong file, phai sort truoc khi tinh chuoi thoi gian.
- `His_435` — do phu chi 46.94% (mat 4733.36 gio).
- `His_435` — du lieu KHONG sap xep theo thoi gian trong file, phai sort truoc khi tinh chuoi thoi gian.
- `His_436` — do phu chi 47.34% (mat 4757.48 gio).
- `His_436` — du lieu KHONG sap xep theo thoi gian trong file, phai sort truoc khi tinh chuoi thoi gian.
- `His_437` — do phu chi 47.9% (mat 4578.23 gio).
- `His_437` — du lieu KHONG sap xep theo thoi gian trong file, phai sort truoc khi tinh chuoi thoi gian.
- `His_471` — du lieu KHONG sap xep theo thoi gian trong file, phai sort truoc khi tinh chuoi thoi gian.
- `His_473` — du lieu KHONG sap xep theo thoi gian trong file, phai sort truoc khi tinh chuoi thoi gian.
- `His_475` — du lieu KHONG sap xep theo thoi gian trong file, phai sort truoc khi tinh chuoi thoi gian.
- `His_477` — du lieu KHONG sap xep theo thoi gian trong file, phai sort truoc khi tinh chuoi thoi gian.
- `His_T1` — du lieu KHONG sap xep theo thoi gian trong file, phai sort truoc khi tinh chuoi thoi gian.
- `His_TUC41` — 3 timestamp trung lap.
- `His_TUC41` — du lieu KHONG sap xep theo thoi gian trong file, phai sort truoc khi tinh chuoi thoi gian.
- `His_report` — du lieu KHONG sap xep theo thoi gian trong file, phai sort truoc khi tinh chuoi thoi gian.
- `Weather` — du lieu KHONG sap xep theo thoi gian trong file, phai sort truoc khi tinh chuoi thoi gian.

## 4. Kiem chung chu ky ngay/dem (xac nhan mui gio)

Trung binh theo gio dia phuong (UTC+7). Buc xa phai dinh quanh 11h-13h; neu lech thi mui gio dang sai.

**His_131**

| Cot | Vai tro | Gio dinh (local) | Gia tri dinh | TB ban dem (0-4h) |
|---|---|---|---|---|
| Substation_Level_110kV_Bay131_MEAS_P | active_power | 12h | 24.76 | 0.071 |

**His_431**

| Cot | Vai tro | Gio dinh (local) | Gia tri dinh | TB ban dem (0-4h) |
|---|---|---|---|---|
| Substation_Level_22kV_Bay431_MEAS_P | active_power | 12h | 24.78 | 0.000 |

**His_431A**

| Cot | Vai tro | Gio dinh (local) | Gia tri dinh | TB ban dem (0-4h) |
|---|---|---|---|---|
| Substation_Level_22kV_Bay431A_MEAS_P | active_power | 14h | 206.49 | 0.000 |

**His_432**

| Cot | Vai tro | Gio dinh (local) | Gia tri dinh | TB ban dem (0-4h) |
|---|---|---|---|---|
| Substation_Level_22kV_Bay432_MEAS_P | active_power | 12h | 3.97 | 0.000 |

**His_433**

| Cot | Vai tro | Gio dinh (local) | Gia tri dinh | TB ban dem (0-4h) |
|---|---|---|---|---|
| Substation_Level_22kV_Bay433_MEAS_P | active_power | 12h | 4.08 | 0.001 |

**His_434**

| Cot | Vai tro | Gio dinh (local) | Gia tri dinh | TB ban dem (0-4h) |
|---|---|---|---|---|
| Substation_Level_22kV_Bay434_MEAS_P | active_power | 12h | 3.98 | 0.000 |

**His_435**

| Cot | Vai tro | Gio dinh (local) | Gia tri dinh | TB ban dem (0-4h) |
|---|---|---|---|---|
| Substation_Level_22kV_Bay435_MEAS_P | active_power | 12h | 3.99 | 0.000 |

**His_436**

| Cot | Vai tro | Gio dinh (local) | Gia tri dinh | TB ban dem (0-4h) |
|---|---|---|---|---|
| Substation_Level_22kV_Bay436_MEAS_P | active_power | 12h | 4.01 | 0.000 |

**His_437**

| Cot | Vai tro | Gio dinh (local) | Gia tri dinh | TB ban dem (0-4h) |
|---|---|---|---|---|
| Substation_Level_22kV_Bay437_MEAS_P | active_power | 12h | 1.51 | nan |

**His_471**

| Cot | Vai tro | Gio dinh (local) | Gia tri dinh | TB ban dem (0-4h) |
|---|---|---|---|---|
| Substation_Level_22kV_Bay471_Meas_P | active_power | 12h | 8.09 | 0.000 |

**His_473**

| Cot | Vai tro | Gio dinh (local) | Gia tri dinh | TB ban dem (0-4h) |
|---|---|---|---|---|
| Substation_Level_22kV_Bay473_Meas_P | active_power | 12h | 4.07 | 0.000 |

**His_475**

| Cot | Vai tro | Gio dinh (local) | Gia tri dinh | TB ban dem (0-4h) |
|---|---|---|---|---|
| Substation_Level_22kV_Bay475_Meas_P | active_power | 12h | 5.46 | 0.000 |

**His_477**

| Cot | Vai tro | Gio dinh (local) | Gia tri dinh | TB ban dem (0-4h) |
|---|---|---|---|---|
| Substation_Level_22kV_Bay477_Meas_P | active_power | 12h | 7.96 | 0.000 |

**His_report**

| Cot | Vai tro | Gio dinh (local) | Gia tri dinh | TB ban dem (0-4h) |
|---|---|---|---|---|
| SOLAR_WS_Rad_2 | irradiance | 12h | 727.31 | 25.776 |
| SOLAR_WS_Rad_1 | irradiance | 12h | 701.07 | 0.011 |
| IEC104S_IEC104S_AO_A0_P_SETPOINT | active_power | 12h | 24.54 | 0.649 |
| IEC104S_IEC104S_AI_P_HIGH | active_power | 12h | 26.64 | 0.569 |

> [!] `His_report.SOLAR_WS_Rad_2` ban dem trung binh 25.8 W/m2 (dang le ~0) — cam bien bi lech zero (offset), phai hieu chinh.

**Weather**

| Cot | Vai tro | Gio dinh (local) | Gia tri dinh | TB ban dem (0-4h) |
|---|---|---|---|---|
| SOLAR_WS_Rad_2 | irradiance | 12h | 732.07 | 26.052 |
| SOLAR_WS_Rad_1 | irradiance | 12h | 703.58 | 0.011 |
| IEC104S_IEC104S_AO_A0_P_SETPOINT | active_power | 12h | 24.66 | 0.649 |
| IEC104S_IEC104S_AI_P_HIGH | active_power | 12h | 26.75 | 0.576 |

> [!] `Weather.SOLAR_WS_Rad_2` ban dem trung binh 26.1 W/m2 (dang le ~0) — cam bien bi lech zero (offset), phai hieu chinh.

## 5. Tuong quan buc xa <-> cong suat

Tuong quan Pearson. Voi PV, |r| giua buc xa va cong suat AC thuong > 0.9.

**His_report**

|                   |   IEC104S_IEC104S_AO_A0_P_SETPOINT |   IEC104S_IEC104S_AI_P_HIGH |   IEC104S_IEC104S_AI_P_LOW |   Substation_Level_22kV_Bay477_Meas_P |   Substation_Level_22kV_Bay475_Meas_P |
|:------------------|-----------------------------------:|----------------------------:|---------------------------:|--------------------------------------:|--------------------------------------:|
| SOLAR_WS_Rad_2    |                              0.916 |                       0.971 |                        nan |                                 0.862 |                                 0.856 |
| SOLAR_WS_Rad_1    |                              0.948 |                       0.988 |                        nan |                                 0.958 |                                 0.952 |
| SOLAR_WSRT1_Rad_1 |                              0.943 |                       0.986 |                        nan |                                 0.95  |                                 0.945 |

**Weather**

|                |   IEC104S_IEC104S_AO_A0_P_SETPOINT |   IEC104S_IEC104S_AI_P_HIGH |   IEC104S_IEC104S_AI_P_LOW |   IEC104S_IEC104S_SI_P_P_MW_MODE |
|:---------------|-----------------------------------:|----------------------------:|---------------------------:|---------------------------------:|
| SOLAR_WS_Rad_2 |                              0.916 |                       0.971 |                        nan |                           -0.005 |
| SOLAR_WS_Rad_1 |                              0.949 |                       0.988 |                        nan |                           -0.006 |
| Data_WS2_Rad_2 |                            nan     |                     nan     |                        nan |                          nan     |

## 6. De xuat buoc tiep theo

- Bang co do phan giai min nhat: **His_131** (~60s). Do phan giai nay quyet dinh chuc nang du bao nao kha thi.
- Tong pham vi thoi gian dai nhat: **His_431A** (376.69 ngay). Duoi ~365 ngay thi mo hinh khong hoc duoc chu ky mua.
- Cot muc tieu du bao nen la cong suat tai diem dau noi (bang cua bay 110kV), khong phai tong cac bay 22kV, tru khi da doi chieu.
- Cac cot co `pct_zero` rat cao can lam ro: la NULL bi ghi thanh 0 hay tag chua dau day. Theo yeu cau FR-04, du lieu trong PHAI giu trang thai thieu, khong duoc gan 0.
- Resample len 15 phut (cho FC-02) chi duoc phep tu du lieu min hon; kiem tra lai cot `nominal_interval_s` o bang 1.