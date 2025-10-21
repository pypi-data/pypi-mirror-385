# 此文件中用于存放各种接口的字典数据


""" get_price(行情数据) 相关数据字典 """
# 频率字典--用于存放不同品种不同周期的K线类型
get_price_frequency_dict = {
    "future": {
        "d": "bar",
        "min": "bar",
        "min_gtja": "bar",
        "tick_l1": "tick",
        "tick_l2": "tick"
    },
    "option": {
        "d": "bar",
        "min": "bar",
        "tick": "tick"
    }
}

# 不同类型的数据需要返回的字段
get_price_data_type_dict = {
    "bar": {'trading_day': 'trading_day', 'trade_time': 'datetime', 'exchange_id': 'exchange_id',
            'instrument_id': 'order_book_ids', 'open_price': 'open', 'highest_price': 'high',
            'lowest_price': 'low', 'close_price': 'close', 'settlement_price': 'settlement',
            'upper_limit_price': 'limit_up', 'lower_limit_price': 'limit_down',
            'pre_settlement_price': 'prev_settlement',
            'volume': 'volume', 'turnover': 'total_turnover', 'open_interest': 'open_interest'},

    "tick": {'trading_day': 'trading_day', 'trade_time': 'datetime', 'exchange_id': 'exchange_id',
             'instrument_id': 'order_book_ids', 'last_price': 'last', 'open_price': 'open',
             'highest_price': 'high', 'lowest_price': 'low', 'close_price': 'close',
             'settlement_price': 'settlement', 'upper_limit_price': 'limit_up',
             'lower_limit_price': 'limit_down', 'pre_settlement_price': 'prev_settlement',
             'pre_close_price': 'prev_close', 'volume': 'volume', 'turnover': 'total_turnover',
             'open_interest': 'open_interest', 'ask_price1': 'a1', 'ask_price2': 'a2', 'ask_price3': 'a3',
             'ask_price4': 'a4', 'ask_price5': 'a5', 'ask_volume1': 'a1_v', 'ask_volume2': 'a2_v',
             'ask_volume3': 'a3_v', 'ask_volume4': 'a4_v', 'ask_volume5': 'a5_v', 'bid_price1': 'b1',
             'bid_price2': 'b2', 'bid_price3': 'b3', 'bid_price4': 'b4', 'bid_price5': 'b5',
             'bid_volume1': 'b1_v', 'bid_volume2': 'b2_v', 'bid_volume3': 'b3_v', 'bid_volume4': 'b4_v',
             'bid_volume5': 'b5_v'},

    "1min_gtja": {'trading_day': 'trading_day', 'trade_time': 'datetime',
                  'instrument_id': 'order_book_ids', 'open_price': 'open', 'highest_price': 'high',
                  'lowest_price': 'low', 'close_price': 'close',
                  # 'upper_limit_price': 'limit_up', 'lower_limit_price': 'limit_down',
                  # 'pre_settlement_price': 'prev_settlement',
                  'volume': 'volume', 'turnover': 'total_turnover', 'open_interest': 'open_interest'}
}

""" get_instruments(合约基础信息) 相关数据字典 """
# 不同合约类型对应的字段
''' t_optinstrument、t_futinstrument(原数据中台给出的表对应的字段) '''
# get_instruments_type_dict = {
#     "future": {
#         "instrumentid": "order_book_id", "exchangeid": "exchange",
#         # "commodity": "commodity",
#         "opendate": "listed_date", "expiredate": "maturity_date", "startdelivdate": "start_delivery_date",
#         "enddelivdate": "end_delivery_date", "delistingdate": "de_listed_date",
#         "volumemultiple": "contract_multiplier", "targetinstrid": "underlying_order_book_id",
#         # "targetinstrid": "underlying_order_book_id", "volumemultiple": "contract_multiplier"
#         # "trading_hour": "trading_hour"
#     },
#
#     "option": {
#         "instrumentid": "order_book_id", "exchangeid": "exchange",
#         # "": "commodity",
#         "opendate": "listed_date", "expiredate": "maturity_date", "deliverymonth": "delivery_month",
#         "startdelivdate": "start_delivery", "enddelivdate": "end_delivery", "delistingdate": "de_listed_date",
#         "optionstype": "option_type", "strikeprice": "strike_price", "targetinstrid": "underlying_order_book_id",
#         "volumemultiple": "contract_multiplier",
#         # "trading_hour": "trading_hour"
#     },
#
#     "future_return_fields": [
#         "order_book_id", "commodity", "listed_date", "de_listed_date", "type", "contract_multiplier",
#         "underlying_order_book_id",
#         "maturity_date", "exchange", "start_delivery_date", "end_delivery_date", "trading_hour"
#     ],
#
#     "option_return_fields": [
#         "order_book_id", "commodity", "listed_date", "de_listed_date", "type", "contract_multiplier",
#         "underlying_order_book_id",
#         "maturity_date", "exchange", "strike_price", "option_type", "exercise_type", "delivery_month", "start_delivery",
#         "end_delivery",
#         "trading_hour"
#     ]
# }

''' t_futinstrument_v2、t_optinstrument_v2 （原数据中台未给出的表） '''
# get_instruments_type_dict = {
#     "future": {
#         "instrument_id": "order_book_id", "exchangeid": "exchange",
#         # "commodity": "commodity",
#         "opendate": "listed_date", "expiredate": "maturity_date", "startdelivdate": "start_delivery_date",
#         "enddelivdate": "end_delivery_date", "delistingdate": "de_listed_date",
#         "volumemultiple": "contract_multiplier", "targetinstrid": "underlying_order_book_id",
#         # "targetinstrid": "underlying_order_book_id", "volumemultiple": "contract_multiplier"
#         # "trading_hour": "trading_hour"
#     },
#
#     "option": {
#         "instrument_id": "order_book_id", "exchangeid": "exchange",
#         # "": "commodity",
#         "opendate": "listed_date", "expiredate": "maturity_date", "deliverymonth": "delivery_month",
#         "startdelivdate": "start_delivery", "enddelivdate": "end_delivery", "delistingdate": "de_listed_date",
#         "optionstype": "option_type", "strikeprice": "strike_price", "targetinstrid": "underlying_order_book_id",
#         "volumemultiple": "contract_multiplier",
#         # "trading_hour": "trading_hour"
#     },
#
#     "future_return_fields": [
#         "order_book_id", "commodity", "listed_date", "de_listed_date", "type", "contract_multiplier",
#         "underlying_order_book_id",
#         "maturity_date", "exchange", "start_delivery_date", "end_delivery_date", "trading_hour"
#     ],
#
#     "option_return_fields": [
#         "order_book_id", "commodity", "listed_date", "de_listed_date", "type", "contract_multiplier",
#         "underlying_order_book_id",
#         "maturity_date", "exchange", "strike_price", "option_type", "exercise_type", "delivery_month", "start_delivery",
#         "end_delivery",
#         "trading_hour"
#     ]
# }


# 不同合约类型对应的字段

''' qc_optinstrument、qc_futinstrument（行情中心新表及对应字段）'''
get_instruments_type_dict = {
    "future": {
        "instrument_id": "order_book_id", "exchange_id": "exchange",
        # "mk_instrument_id": "order_book_id", "exchange_id": "exchange",
        # "commodity": "commodity",
        "open_date": "listed_date", "expire_date": "maturity_date", "start_deliv_date": "start_delivery_date",
        "end_deliv_date": "end_delivery_date", "delisting_date": "de_listed_date",
        "volume_multiple": "contract_multiplier", "underlying_instrument_id": "underlying_order_book_id",
        # "underlying_instrument_id": "underlying_order_book_id", "volume_multiple": "contract_multiplier"
        # "trading_hour": "trading_hour"
    },

    "option": {
        "instrument_id": "order_book_id", "exchange_id": "exchange",
        # "": "commodity",
        "open_date": "listed_date", "expire_date": "maturity_date", "delivery_month": "delivery_month",
        "start_deliv_date": "start_delivery", "end_deliv_date": "end_delivery", "delisting_date": "de_listed_date",
        "option_stype": "option_type", "strike_price": "strike_price",
        "underlying_instrument_id": "underlying_order_book_id",
        "volume_multiple": "contract_multiplier",
        # "trading_hour": "trading_hour"
    },

    "future_return_fields": [
        "order_book_id", "commodity", "listed_date", "de_listed_date", "type", "contract_multiplier",
        "underlying_order_book_id",
        "maturity_date", "exchange", "start_delivery_date", "end_delivery_date", "trading_hour"
    ],

    "option_return_fields": [
        "order_book_id", "commodity", "listed_date", "de_listed_date", "type", "contract_multiplier",
        "underlying_order_book_id",
        "maturity_date", "exchange", "strike_price", "option_type", "exercise_type", "delivery_month", "start_delivery",
        "end_delivery",
        "trading_hour"
    ]
}

""" 期货交割手续费---相关数据字典 """
# 期货交割手续费--返回结果字段
# qc_nexttradeparam
future_delivery_fee_return_fields = ["instrument_id", "product_id", "exchange_id", "trading_day", "open_ratio_by_money",
                                     "open_ratio_by_volume", "close_ratio_by_money", "close_ratio_by_volume",
                                     "close_today_ratio_by_money", "close_today_ratio_by_volume"]

# qc_future_tradeparam
# future_delivery_fee_return_fields = ["mk_instrument_id", "trading_day", "open_commission",
#                                      "close_commission", "close_commission_today"]

# 期货交割手续费--返回结果字段重命名
# qc_nexttradeparam
future_delivery_fee_return_fields_rename = {"instrument_id": "order_book_id", "product_id": "commodity",
                                            "exchange_id": "exchange", "trading_day": "date",
                                            "open_ratio_by_money": "open_transaction_fee_amount",
                                            "open_ratio_by_volume": "open_transaction_fee_s",
                                            "close_ratio_by_money": "close_transaction_fee_amount",
                                            "close_ratio_by_volume": "close_transaction_fee_s",
                                            "close_today_ratio_by_money": "close_today_fee_amount",
                                            "close_today_ratio_by_volume": "close_today_fee_s"}

# qc_future_tradeparam
# future_delivery_fee_return_fields_rename = {
#                                             "mk_instrument_id": "order_book_id", "commodity": "commodity",
#                                             "trading_day": "date",
#                                             "open_commission": "open_transaction_fee_amount",
#                                             # "open_ratio_by_volume": "open_transaction_fee_s",
#                                             "close_commission": "close_transaction_fee_amount",
#                                             # "close_ratio_by_volume": "close_transaction_fee_s",
#                                             "close_commission_today": "close_today_fee_amount",
#                                             # "close_today_ratio_by_volume": "close_today_fee_s"
#                                             }

""" 期货保证金 """
# 期货保证金--返回结果字段
# qc_nexttradeparam
future_margin_ratio_return_fields = ["instrument_id", "trading_day", "product_id", "exchange_id", "s_long_mrg_rate",
                                     "s_short_mrg_rate", "h_long_mrg_rate", "h_short_mrg_rate"]

# qc_future_tradeparam
# 缺失字段：交易所， 投机买保证金率， 投机卖保证金率， 套保买保证金率， 套保卖保证金率
# future_margin_ratio_return_fields = ["mk_instrument_id", "trading_day"]

# 期货保证金--返回结果字段重命名
# qc_nexttradeparam
future_margin_ratio_return_fields_rename = {
    "instrument_id": "order_book_id", "commodity": "commodity",
    "trading_day": "date",
    "product_id": "commodity",
    "exchange_id": "exchange",
    "s_long_mrg_rate": "s_buy_margin",
    "s_short_mrg_rate": "s_sell_margin",
    "h_long_mrg_rate": "h_buy_margin",
    "h_short_mrg_rate": "h_sell_margin"
}

# qc_future_tradeparam
# future_margin_ratio_return_fields_rename = {
#                                             "mk_instrument_id": "order_book_id", "commodity": "commodity",
#                                             "trading_day": "date",
#                                             # "交易所": "exchange",
#                                             # "投机买保证金率": "s_buy_margin",
#                                             # "投机卖保证金率": "s_sell_margin",
#                                             # "套保买保证金率": "h_buy_margin",
#                                             # "套保卖保证金率": "h_sell_margin"
#                                             }


""" 期货限仓数据 """
# 期货限仓数据--返回结果字段
# qc_nexttradeparam
future_limit_position_return_fields = ["instrument_id", "trading_day", "product_id", "exchange_id", "pos_limit_vol"]

# qc_future_tradeparam
# 缺失字段：交易所， 持仓限额
# future_limit_position_return_fields = ["mk_instrument_id", "trading_day"]

# 期货保证金--返回结果字段重命名
# qc_nexttradeparam
future_limit_position_return_fields_rename = {
    "instrument_id": "order_book_id", "product_id": "commodity",
    "trading_day": "date",
    "exchange_id": "exchange",
    "pos_limit_vol": "limit_position"
}

# qc_future_tradeparam
# 缺失字段：交易所， 持仓限额
# future_limit_position_return_fields_rename = {
#                                             "mk_instrument_id": "order_book_id", "commodity": "commodity",
#                                             "trading_day": "date",
#                                             # "交易所": "exchange",
#                                             # "持仓限额": "limit_position"
#                                             }


# 主力合约

""" 主力合约 """
# 主力合约--返回结果字段--dayk、mink
main_contract_return_fields = ["trading_day", "trade_time", "exchange_id", "instrument_id", "open_price", "close_price",
                               "highest_price", "lowest_price", "upper_limit_price", "lower_limit_price",
                               "settlement_price",
                               "pre_settlement_price", "pre_close_price", "turnover", "volume",
                               "open_interest", "total_open_interest", "total_volume", "insert_time",
                               "prev_close_spread", "open_spread", "prev_close_ratio", "open_ratio"]

# 主力合约--返回结果字段重命名--dayk、mink
main_contract_return_fields_rename = {
    "trading_day": "trading_day",
    "trade_time": "datetime",
    "exchange_id": "exchange_id",
    "instrument_id": "order_book_ids",
    "open_price": "open",
    "close_price": "close",
    "highest_price": "high",
    "lowest_price": "low",
    "upper_limit_price": "limit_up",
    "lower_limit_price": "limit_down",
    "settlement_price": "settlement",
    "pre_settlement_price": "prev_settlement",
    "pre_close_price": "prev_close",
    "turnover": "total_turnover",
    "volume": "volume",
    "open_interest": "open_interest",
    "total_open_interest": "total_open_interest",
    "total_volume": "total_volume",
    "insert_time": "insert_time",

}


# 主力合约--返回结果字段--gtja_mink
gtja_mink_main_contract_return_fields = ["trading_day", "trade_time", "trade_timestamp",
                                         "exchange_id", "instrument_id", "open_price", "close_price",
                               "highest_price", "lowest_price", "upper_limit_price", "lower_limit_price",
                               "settlement_price",
                               "pre_settlement_price", "turnover", "volume",
                               "open_interest", "insert_time", "product_id"
                               ]
                               # "prev_close_spread", "open_spread", "prev_close_ratio", "open_ratio", 'pre_close_price']

# 主力合约--返回结果字段重命名--gtja_mink
gtja_mink_main_contract_return_fields_rename = {
    "trading_day": "trading_day",
    "trade_time": "datetime",
    "exchange_id": "exchange_id",
    "instrument_id": "order_book_ids",
    "open_price": "open",
    "close_price": "close",
    "highest_price": "high",
    "lowest_price": "low",
    "upper_limit_price": "limit_up",
    "lower_limit_price": "limit_down",
    "settlement_price": "settlement",
    "pre_settlement_price": "prev_settlement",
    # "pre_close_price": "prev_close",
    "turnover": "total_turnover",
    "volume": "volume",
    "open_interest": "open_interest",
    # "total_open_interest": "total_open_interest",
    # "total_volume": "total_volume",
    "insert_time": "insert_time",

}



tick_main_contract_return_fields = ["trading_day", "trade_time", "exchange_id", "instrument_id", "open_price",
                                    "highest_price", "lowest_price", "last_price", "upper_limit_price", "lower_limit_price",
                                    "pre_settlement_price", "pre_close_price", "volume",
                                    "open_interest", "turnover",
                                    "ask_price1", "ask_price2", "ask_price3", "ask_price4", "ask_price5",
                                    "ask_volume1", "ask_volume2", "ask_volume3", "ask_volume4", "ask_volume5",
                                    "bid_price1", "bid_price2", "bid_price3", "bid_price4", "bid_price5",
                                    "bid_volume1", "bid_volume2", "bid_volume3", "bid_volume4", "bid_volume5",
                                    "insert_time"]

# 主力合约--返回结果字段重命名
tick_main_contract_return_fields_rename = {
    "trading_day": "trading_day",
    "trade_time": "datetime",
    "exchange_id": "exchange_id",
    "instrument_id": "order_book_ids",
    "open_price": "open",
    "highest_price": "high",
    "lowest_price": "low",
    "last_price": "last",
    "upper_limit_price": "limit_up",
    "lower_limit_price": "limit_down",
    "pre_settlement_price": "prev_settlement",
    "pre_close_price": "prev_close",
    "volume": "volume",
    "open_interest": "open_interest",
    'ask_price1': 'a1',
    'ask_price2': 'a2',
    'ask_price3': 'a3',
    'ask_price4': 'a4',
    'ask_price5': 'a5',
    'ask_volume1': 'a1_v',
    'ask_volume2': 'a2_v',
    'ask_volume3': 'a3_v',
    'ask_volume4': 'a4_v',
    'ask_volume5': 'a5_v',
    'bid_price1': 'b1',
    'bid_price2': 'b2',
    'bid_price3': 'b3',
    'bid_price4': 'b4',
    'bid_price5': 'b5',
    'bid_volume1': 'b1_v',
    'bid_volume2': 'b2_v',
    'bid_volume3': 'b3_v',
    'bid_volume4': 'b4_v',
    'bid_volume5': 'b5_v',
    "insert_time": "insert_time",

}
