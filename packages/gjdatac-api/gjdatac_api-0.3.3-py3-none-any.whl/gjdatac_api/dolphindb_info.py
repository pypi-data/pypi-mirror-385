# 此文件用于存放dolphinDB的相关信息，包括登录信息、数据库和表信息等。


""" 行情数据所在数据库和表 """

''' 期货 '''
# 历史期货行情数据 L1-tick数据
history_future_tick_db_path = "dfs://tick"  # 数据库路径
# history_future_tick_db_table_name = "ctp_future_tick"  # 表名（旧）
history_future_tick_db_table_name = "qc_future_tick"  # 表名

# 历史期货行情数据 L2-tick数据
history_future_tick_l2_db_path = "dfs://tick_level2"  # 数据库路径
# history_future_tick_l2_db_table_name = "t_future_tick"  # 表名(旧)
history_future_tick_l2_db_table_name = "qc_future_tick_level2"  # 表名（新）

# 历史期货行情 L1-分钟k线
history_future_min_db_path = "dfs://minutek"  # 数据库路径
# history_future_min_db_table_name = "ctp_future_mink"  # 表名(旧)
history_future_min_db_table_name = "qc_future_mink"  # 表名

# 历史期货行情 L1-日k线
history_future_day_db_path = "dfs://dayk"  # 数据库路径
# history_future_day_db_table_name = "ctp_future_dayk"  # 表名（旧）
history_future_day_db_table_name = "qc_future_dayk"  # 表名

# 历史期货实时分钟k线合成数据  1min_gtja
# history_future_1min_gtja_db_path = "dfs://minutek"  # 数据库路径 (旧)
# history_future_1min_gtja_db_table_name = "t_trade_future_mink"  # 表名 (旧)
history_future_1min_gtja_db_path = "dfs://r_minutek"  # 数据库路径 （新）
history_future_1min_gtja_db_table_name = "qc_trade_future_mink"  # 表名

''' 期权 '''
# 历史期权行情数据 tick数据
history_option_tick_db_path = "dfs://tick"  # 数据库路径
# history_option_tick_db_table_name = "ctp_option_tick"  # 表名（旧）
history_option_tick_db_table_name = "qc_option_tick"  # 表名


# 历史期权行情数据 分钟k线
history_option_min_db_path = "dfs://minutek"   # 数据库路径
# history_option_min_db_table_name = "ctp_option_mink"  # 表名
history_option_min_db_table_name = "qc_option_mink"  # 表名


# 历史期权行情数据 日k线
history_option_day_db_path = "dfs://dayk"  # 数据库路径
# history_option_day_db_table_name = "ctp_option_dayk"  # 表名（旧）
history_option_day_db_table_name = "qc_option_dayk"  # 表名

""" 基础信息 """

# 交易参数
trading_params_db_path = "dfs://basicinfo"  # 数据库路径
# trading_params_db_table_name = "t_nexttradeparam"  # 表名
trading_params_db_table_name = "qc_nexttradeparam"  # 表名
# trading_params_db_table_name = "qc_future_tradeparam"  # 表名

# 期货-合约信息
future_contract_db_path = "dfs://basicinfo"  # 数据库路径
# future_contract_db_table_name = "t_futinstrument"  # 表名（原数据中台给出）
# future_contract_db_table_name = "t_futinstrument_v2"  # 表名（原数据中台未给出）
future_contract_db_table_name = "qc_futinstrument"  # 表名（新）

# 期权-合约信息
option_contract_db_path = "dfs://basicinfo"  # 数据库路径
# option_contract_db_table_name = "t_optinstrument"  # 表名（原数据中台给出的表）
# option_contract_db_table_name = "t_optinstrument_v2"  # 表名（原数据中台未给出）
option_contract_db_table_name = "qc_optinstrument"  # 表名(行情中心)

# 交易日历
trading_dates_db_path = "dfs://basicinfo"  # 数据库路径
# trading_dates_db_table_name = "b_calendar"  # 表名（旧）
trading_dates_db_table_name = "qc_calendar"  # 表名


# twap-分钟
twap_min_db_path = "dfs://minutek"  # 数据库路径
# twap_min_db_table_name = "t_mink_metric"  # 表名（旧）
twap_min_db_table_name = "qc_min_metric"  # 表名（新）

# twap-天
twap_day_db_path = "dfs://dayk"  # 数据库路径
# twap_day_db_table_name = "t_day_metric"  # 表名（旧）
twap_day_db_table_name = "qc_day_metric"  # 表名（新）

# vwap-分钟
vwap_min_db_path = "dfs://minutek"  # 数据库路径
# vwap_min_db_table_name = "t_mink_metric"  # 表名（旧）
vwap_min_db_table_name = "qc_min_metric"  # 表名（新）

# vwap-天
vwap_day_db_path = "dfs://dayk"  # 数据库路径
# vwap_day_db_table_name = "t_day_metric"  # 表名（旧）
vwap_day_db_table_name = "qc_day_metric"  # 表名(新)

# 仓单数据
get_warehouse_stocks_future_db_path = "dfs://dayk"  # 数据库路径
# get_warehouse_stocks_future_db_table_name = "t_warehouse_stocks"  # 表名（旧）
get_warehouse_stocks_future_db_table_name = "qc_warehouse_stocks"  # 表名（新）

# 主力合约
main_contract_db_path = "dfs://dayk"  # 数据库路径
main_contract_db_table_name = "qc_gtja_future_maincontract"  # 表名

# 主/次力合约
dayk_future_maincontract_db = "dfs://dayk_future_maincontract"
minutek_future_maincontract_db = "dfs://minutek_future_maincontract"
minutek_future_maincontract_gtja_db = "dfs://minutek"

qc_future_maincontract_dayk = "qc_future_maincontract_dayk"
qc_future_maincontract_minutek = "qc_future_maincontract_mink"
qc_future_maincontract_gtja_minutek = "qc_gtja_future_mink"


tick_main_contract_db_path = "dfs://tick"  # 数据库路径
tick_main_contract_db_table_name = "qc_future_tick"  # 表名


# 期货交割手续费(目前需求中所需的字段在交易参数表中都存在，所以直接使用交易参数表)
delivery_fee_db_path = "dfs://basicinfo"  # 数据库路径
delivery_fee_db_table_name = "qc_exch_fut_commrate"  # 表名

# 期货保证金
margin_db_path = "dfs://basicinfo"  # 数据库路径
margin_db_table_name = "qc_future_tradeparam"  # 表名(暂定使用交易参数表)

# 期货限仓数据
limit_position_db_path = "dfs://basicinfo"  # 数据库路径
limit_position_db_table_name = "qc_future_tradeparam"  # 表名(暂定使用交易参数表)

# 现货
spot_db_path = "dfs://basicinfo"  # 数据库路径
spot_db_table_name = "qc_basis"  # 表名

# 基差
basis_db_path = "dfs://basicinfo"  # 数据库路径
basis_db_table_name = "qc_basis"  # 表名

# 库存
inventory_db_path = "dfs://basicinfo"  # 数据库路径
inventory_db_table_name = "qc_product_inventory"  # 表名


# 订阅实时分钟k
subscribe_min_db_table_name = "QcMinKlineTable"  # 表名




