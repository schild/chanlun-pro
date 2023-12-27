#:  -*- coding: utf-8 -*-
from chanlun.exchange.exchange_db import ExchangeDB
from chanlun.exchange.exchange_futu import ExchangeFutu
import traceback
import time

"""
同步股票数据到数据库中
"""

exchange = ExchangeDB("hk")
line_exchange = ExchangeFutu()

# 从自选中获取同步股票 手动指定吧
run_codes = []


for code in run_codes:
    try:
        for f in ["w", "d", "60m", "30m", "15m", "10m", "5m"]:
            time.sleep(3)
            while True:
                last_dt = exchange.query_last_datetime(code, f)
                if last_dt is None:
                    klines = line_exchange.klines(
                        code,
                        f,
                        end_date="2020-01-01 00:00:00",
                        args={"is_history": True},
                    )
                    if len(klines) == 0:
                        klines = line_exchange.klines(
                            code, f, args={"is_history": True}
                        )
                else:
                    klines = line_exchange.klines(
                        code, f, start_date=last_dt, args={"is_history": True}
                    )

                print(f"Run code {code} frequency {f} klines len {len(klines)}")
                exchange.insert_klines(code, f, klines)
                if len(klines) <= 1:
                    break

    except Exception as e:
        print(f"执行 {code} 同步K线异常")
        print(e)
        print(traceback.format_exc())
        time.sleep(10)
