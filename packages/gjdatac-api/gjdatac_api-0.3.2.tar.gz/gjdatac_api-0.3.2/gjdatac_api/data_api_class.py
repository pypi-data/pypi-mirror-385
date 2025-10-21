# 此文件用于编写数据接口---类方式实现


import re
import datetime
import operator
import asyncio

import holidays
import chinese_calendar as calendar
import pandas as pd
import dolphindb as ddb

from utils.dict_data import (get_price_frequency_dict, get_price_data_type_dict, get_instruments_type_dict,
                        future_delivery_fee_return_fields, future_delivery_fee_return_fields_rename,
                        future_margin_ratio_return_fields, future_margin_ratio_return_fields_rename,
                        future_limit_position_return_fields, future_limit_position_return_fields_rename,
                        main_contract_return_fields, main_contract_return_fields_rename,
                        tick_main_contract_return_fields, tick_main_contract_return_fields_rename,
                        gtja_mink_main_contract_return_fields, gtja_mink_main_contract_return_fields_rename
                        )
from utils.dolphindb_info import *
from utils.instrument_class import Instrument


class GJDataC:

    def __init__(self, host, port, user_id, password, dolphindb_service=None):
        """
        用于定义一些不同接口所需的变量以及一些初始化操作
        :param host: 数据库地址
        :param port: 数据库端口
        :param user_id: 数据库用户名
        :param password: 数据库密码

        用户调用api时，需要提供dolphindb相关的用户信息，包括host、port、user_id、password，用于连接数据库
        """

        ''' 初始化校验 '''
        # 数据库参数
        self.host = host
        self.port = port
        self.user_id = user_id
        self.password = password

        # 创建向量，包含所有可用节点的地址和端口
        self.sites = dolphindb_service

    def connect_db(self, table_name, db_path):
        """
        此方法用于根据不同的数据表及数据库获取数据，只返回Table对象，对应的数据处理在对应的数据接口处理
        :param table_name: 数据表路径
        :param db_path: 数据库路径
        :return 根据数据库和表路径获取的数据(Table对象), 会话信息(db_session)
        """

        # 连接数据库
        db_session = ddb.session()
        # 原始方式
        if not self.sites:
            success = db_session.connect(self.host, self.port, self.user_id, self.password)
        else:
            # 创建连接；开启高可用，并指定sites为所有可用节点的ip:port
            success = db_session.connect(self.host, self.port, self.user_id, self.password, highAvailability=True,
                                         highAvailabilitySites=self.sites)
        if not success:
            raise Exception("please check your database connection information")

        # 从数据库中获取数据
        data = db_session.loadTable(tableName=table_name, dbPath=db_path)

        return data, db_session

    """ 通用方法 """

    @staticmethod
    def general_validate_params_required(param, param_name):
        """
        校验参数是否必填
        :param param: 参数值
        :param param_name: 参数名称
        :return: None （用于校验数据无需返回值）
        """
        if not param:
            raise ValueError(f"{param_name} is required")

    @staticmethod
    def general_validate_either_or(field_1_name, field_1_value, field_2_name, field_2_value):
        """
        此方法用于验证二选一的参数填写情况
        :param field_1_name: 参数1名称
        :param field_1_value: 参数1值
        :param field_2_name: 参数2名称
        :param field_2_value: 参数2值
        :return: None （用于校验数据无需返回值）
        """
        if not field_1_value and not field_2_value:
            raise ValueError(f"{field_1_name} or {field_2_name} is required")
        if field_1_value and field_2_value:
            raise ValueError(f"{field_1_name} and {field_2_name} cannot be both provided")

    def general_validate_date(self, date_str):
        """
        判断字符串是否为datetime.date, datetime.datetime格式。
        :param date_str: 待判断的字符串。

        Returns:
            True: 如果是日期格式，返回 True。
            False: 否则返回 False。
        """
        if not self.general_validate_date_str_is_datetime_type(date_str):
            return self.general_validate_date_str_is_date_type(date_str)
        return True

    @staticmethod
    def general_validate_date_str_is_datetime_type(date_data):
        """
        此方法用于验证日期字段是否为可以转换为datetime的类型
        :param date_data: 日期字符串

        :return : 如果可以转换为datetime类型，返回 True, 否则返回 False。
        """

        try:
            datetime.datetime.strptime(date_data, '%Y-%m-%d %H:%M:%S')
            return True
        except ValueError:
            return False

    @staticmethod
    def general_validate_date_str_is_date_type(date_data):
        """
        此方法用于验证日期字段是否为可以转换为date的类型
        :param date_data: 日期字符串

        :return : 如果可以转换为date类型，返回 True, 否则返回 False。
        """

        try:
            datetime.datetime.strptime(date_data, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    @staticmethod
    def general_validate_field_str_or_list(field_value, field_name):
        """
        对参数的类型进行校验，判断是否为字符串或字符串列表。
        :param field_value: 待校验的参数值。
        :param field_name: 待校验的参数名称。
        :return: None （用于校验数据无需返回值）
        """

        if field_value and not isinstance(field_value, (str, list)):
            raise ValueError(f"{field_name} should be a string or a list of strings")

    @staticmethod
    def general_validate_param_is_str(param_name, param_value):
        """
        校验参数是否为str类型
        :param param_name: 参数名称
        :param param_value: 参数值

        :return: None （用于校验数据无需返回值）
        """

        if not isinstance(param_value, str):
            raise ValueError(f"{param_name} type error, please input str type")

    def general_validate_asset_type(self, asset_type):
        """
        对asset_type进行校验
        :param asset_type: str, 合约类型

        :return: None （用于校验数据无需返回值）
        """
        self.general_validate_params_required(asset_type, "asset_type")  # 校验必填参数
        if not isinstance(asset_type, str):
            raise ValueError("asset_type should be a string")
        if asset_type not in ["future", "option"]:
            raise ValueError("asset_type should be 'future' or 'option'")

    def general_validate_fields(self, data, fields):
        """
        根据用户选择的字段进行字段筛选
        :param fields: 字段列表--用户传入的需要返回的字段
        :param data: 数据

        :return data: 根据用户填写的字段筛选后的数据
        """

        ''' 校验fields '''
        # 如果没有传入fields, 则返回所有字段
        if not fields:
            return data
        self.general_validate_field_str_or_list(fields, "fields")

        ''' 根据fields进行处理 '''
        # 如果传入了fields，则根据传入的fields进行处理
        columns_list = data.columns.tolist()

        if isinstance(fields, str):
            self._deal_fields(fields, columns_list)
            data = data[[fields]]
        elif isinstance(fields, list):
            for field in fields:
                self._deal_fields(field, columns_list)
            data = data[fields]

        return data

    @staticmethod
    def _deal_fields(_field, columns_list):
        """
        判断用户选择的字段是否存在

        :param columns_list: 数据的所有字段

        :return: None （用于校验数据无需返回值）
        """
        if _field not in columns_list:
            raise ValueError(
                f"fields: got invalided value '{_field}', choose any in "
                f"{columns_list}")

    @staticmethod
    def general_filter_data_by_field(data, field_name, field_value):
        """
        根据指定的字段进行数据过滤
        :param data: pandas.DataFrame, 数据
        :param field_name: str, 过滤字段
        :param field_value: str or list, 过滤值

        :return 根据字段过滤后的数据
        """

        return data[data[field_name].isin(field_value)] if isinstance(
            field_value, list) else data[data[field_name] == field_value]

    def _general_filter_data_by_field(self, data, field_name, field_value):
        """
        根据自定字段进行类型校验以及数据筛选
        :param data: 需要处理的数据
        :param field_name: 字段名
        :param field_value: 字段值

        :return : 根据字段过滤后的数据
        """
        self.general_validate_field_str_or_list(field_value, field_name)
        return self.general_filter_data_by_field(data, field_name, field_value)

    def general_date_str_to_date(self, date_str):
        """
        将date类型的str转换成datetime.date类型
        :param date_str: str, 日期字符串
        """
        if not self.general_validate_date_str_is_date_type(date_str):
            raise ValueError("date_str is not a valid date string, please use the format 'YYYY-MM-DD")

        return datetime.datetime.strptime(date_str, "%Y-%m-%d")

    @staticmethod
    def general_date_str_to_datetime(date_str):
        """ 将date类型的str转换成datetime.datetime类型 """
        if isinstance(date_str, str):
            return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    def filter_contract_type(self, instrument_id):
        """
        筛选合约类型
        Args:
            instrument_id: 合约代码
        Returns:
            合约类型，'future' 或 'option'
        """
        # 在期货合约信息表查询
        future_data, bar_db_session = self.connect_db(future_contract_db_table_name, future_contract_db_path)

        # 根据 instrument_id 进行数据查询
        future_query_data = future_data.where(f"instrument_id='{instrument_id}'") if isinstance(instrument_id, str) \
            else future_data.where(f"instrument_id in {instrument_id}")

        # 根据 mk_instrument_id 进行数据筛选
        mk_future_query_data = future_data.where(f"mk_instrument_id='{instrument_id}'") if isinstance(instrument_id,
                                                                                                      str) \
            else (future_data.where(f"mk_instrument_id in {instrument_id}"))

        # 如果在期货合约信息表中的 instrument_id 未查询到，则继续在 mk_instrument_id 查找
        if future_query_data.rows > 0:
            bar_db_session.close()
            return 'future'
        # 如果在 mk_instrument_id 列中也没有查到，那么表示合约代码是期权类型
        elif mk_future_query_data.rows > 0:
            bar_db_session.close()
            return 'future'
        else:
            bar_db_session.close()
            return 'option'

    @staticmethod
    def format_date(input_date):
        """
        将输入的日期转换为指定格式的字符串。

        参数:
            input_date: 输入的日期，可以是 datetime、date 或 str 类型。
                       支持的字符串格式包括：
                       - "YYYY-MM-DD HH:MM:SS"
                       - "YYYY-MM-DD"
                       - "YYYY.MM.DD HH:MM:SS"
                       - "YYYY.MM.DD"

        返回:
            str: 转换后的日期字符串，格式为 "YYYY.MM.DD HH:MM:SS" 或 "YYYY.MM.DD"。
        """
        # 如果输入是 datetime 类型
        if isinstance(input_date, datetime.datetime):
            if input_date.hour == 0 and input_date.minute == 0 and input_date.second == 0:
                return input_date.strftime("%Y.%m.%d")
            else:
                return input_date.strftime("%Y.%m.%d %H:%M:%S")

        # 如果输入是 date 类型
        elif isinstance(input_date, datetime.date):
            return input_date.strftime("%Y.%m.%d")

        # 如果输入是字符串类型
        elif isinstance(input_date, str):
            try:
                # 尝试解析包含时间的格式
                dt = datetime.datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S")
                return dt.strftime("%Y.%m.%d %H:%M:%S")
            except ValueError:
                try:
                    # 尝试解析不包含时间的格式
                    dt = datetime.datetime.strptime(input_date, "%Y-%m-%d")
                    return dt.strftime("%Y.%m.%d")
                except ValueError:
                    try:
                        # 尝试解析包含时间的点分隔格式
                        dt = datetime.datetime.strptime(input_date, "%Y.%m.%d %H:%M:%S")
                        return dt.strftime("%Y.%m.%d %H:%M:%S")
                    except ValueError:
                        try:
                            # 尝试解析不包含时间的点分隔格式
                            dt = datetime.datetime.strptime(input_date, "%Y.%m.%d")
                            return dt.strftime("%Y.%m.%d")
                        except ValueError:
                            raise ValueError("输入的日期格式不支持")

        # 如果输入类型不支持
        else:
            raise TypeError("输入类型必须是 datetime、date 或 对应格式的str")

    @staticmethod
    def format_date_split_by_(input_date):
        """
        将输入的日期转换为指定格式的字符串。

        参数:
            input_date: 输入的日期，可以是 datetime、date 或 str 类型。
                       支持的字符串格式包括：
                       - "YYYY-MM-DD HH:MM:SS"
                       - "YYYY-MM-DD"
                       - "YYYY.MM.DD HH:MM:SS"
                       - "YYYY.MM.DD"

        返回:
            str: 转换后的日期字符串，格式为 "YYYY.MM.DD HH:MM:SS" 或 "YYYY.MM.DD"。
        """
        # 如果输入是 datetime 类型
        if isinstance(input_date, datetime.datetime):
            if input_date.hour == 0 and input_date.minute == 0 and input_date.second == 0:
                return input_date.strftime("%Y-%m-%d")
            else:
                return input_date.strftime("%Y-%m-%d %H:%M:%S")

        # 如果输入是 date 类型
        elif isinstance(input_date, datetime.date):
            return input_date.strftime("%Y-%m-%d")

        # 如果输入是字符串类型
        elif isinstance(input_date, str):
            try:
                # 尝试解析包含时间的格式
                dt = datetime.datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S")
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    # 尝试解析不包含时间的格式
                    dt = datetime.datetime.strptime(input_date, "%Y-%m-%d")
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    try:
                        # 尝试解析包含时间的点分隔格式
                        dt = datetime.datetime.strptime(input_date, "%Y.%m.%d %H:%M:%S")
                        return dt.strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        try:
                            # 尝试解析不包含时间的点分隔格式
                            dt = datetime.datetime.strptime(input_date, "%Y.%m.%d")
                            return dt.strftime("%Y-%m-%d")
                        except ValueError:
                            raise ValueError("输入的日期格式不支持")

        # 如果输入类型不支持
        else:
            raise TypeError("输入类型必须是 datetime、date 或 对应格式的str")

    @staticmethod
    def validate_dates(start_date, end_date):
        """
        校验日期合法性并比较先后关系

        参数:
            start_date: 开始日期(可以是str/datetime/date类型)
            end_date: 结束日期(可以是str/datetime/date类型)

        返回:
            如果日期合法且start_date <= end_date，返回(parsed_start, parsed_end)
            否则返回None
        """

        def parse_date(date_obj):
            """将各种类型的日期统一转换为datetime.datetime对象"""
            if isinstance(date_obj, datetime.datetime):
                return date_obj
            if isinstance(date_obj, datetime.date):
                # 将date转换为datetime，时间部分设为00:00:00
                return datetime.datetime.combine(date_obj, datetime.time.min)
            if not isinstance(date_obj, str):
                return None

            # 移除可能存在的单引号
            date_str = date_obj.strip("'\"")

            # 尝试匹配各种日期格式
            patterns = [
                r'(\d{4})[-.](\d{1,2})[-.](\d{1,2})(?:\s+(\d{1,2}):(\d{1,2}):(\d{1,2}))?',  # 带时间的格式
                r'(\d{4})[-.](\d{1,2})[-.](\d{1,2})',  # 不带时间的格式
                r'(\d{4})(\d{2})(\d{2})'  # 紧凑格式
            ]

            for pattern in patterns:
                match = re.fullmatch(pattern, date_str)
                if match:
                    groups = match.groups()
                    year, month, day = map(int, groups[:3])
                    try:
                        # 如果有时间部分则解析时间，否则设为00:00:00
                        if len(groups) > 3 and all(groups[3:6]):
                            hour, minute, second = map(int, groups[3:6])
                            return datetime.datetime(year, month, day, hour, minute, second)
                        return datetime.datetime(year, month, day)
                    except ValueError:
                        return None
            return None

        # 解析日期（统一转换为datetime对象）
        parsed_start = parse_date(start_date)
        parsed_end = parse_date(end_date)

        # 检查日期是否有效
        if not parsed_start or not parsed_end:
            return None

        # 比较日期时间
        if parsed_start > parsed_end:
            return None

        return (parsed_start, parsed_end)

    """ get_price(获取行情数据接口) """

    def get_price(self, order_book_ids=None, asset_type="future", frequency=None, start_date=None, end_date=None,
                  fields=None, is_batch=False, batch_size=1000000):
        """
        行情数据接口
        :param order_book_ids: 合约代码--必填
        :param asset_type: 合约类型--必填, 默认为--'future'
        :param frequency: 频率--必填
        :param start_date: 开始日期--选填
        :param end_date: 结束日期--选填
        :param fields: 字段列表--选填
        :param is_batch: 是否分批获取--选填, 默认为--True
        :param batch_size: 每次分批获取的条数--选填, 默认为--1000000
        :return: 行情数据
        """

        # # 从数据库获取的数据是Table类型，需要转换为DataFrame类型, 并按照时间进行排序
        # self.get_price_data = self.get_price_data.sort_values(by='datetime', ascending=True)

        ''' 数据校验 (先对必填参数进行校验)'''
        if start_date and end_date:
            if not self.validate_dates(start_date, end_date):
                return None

        # 对order_book_ids进行校验
        self.get_price_validate_order_book_ids(order_book_ids)

        # 对asset_type进行校验
        self.general_validate_asset_type(asset_type)

        # 对frequency进行校验
        self.get_price_validate_frequency(frequency)

        # 对 start_date 和 end_date 进行校验
        self.get_price_validate_start_end_date(start_date, end_date)

        ''' 参数校验完成后，开始根据参数从服务器获取数据 '''
        # 此处获取数据时已经根据order_book_ids筛选过一次数据了，所以后续不需要再对该字段进行筛选
        # data = self.get_price_data_get_data(order_book_ids, asset_type, frequency, start_date, end_date)
        # 从dolphindb获取所有满足条件的数据

        ''' 参数校验完成后再根据参数从dolphindb获取数据 '''
        # 获取数据库地址和表名
        db_table_name = self.get_price_get_db_table_name(asset_type, frequency)

        # 从dolphindb获取所有满足条件的数据
        total_data, db_session = self.get_price_data_get_data(order_book_ids, db_table_name, start_date, end_date)
        print("开始处理数据\n")
        print("总数据量: ", total_data.rows)

        if is_batch:  # 如果需要分批次处理数据
            for i in range(0, total_data.rows, batch_size):
                # 分批次从dolphindb获取数据，转换成dataframe（因为数据量过大时，同时将tables对象转换成dataframe比较耗时）
                data = total_data.limit([i, batch_size]).toDF()

                # 数据处理
                data = self.get_price_by_type_frequency(asset_type, frequency, data)
                data = self.get_price_filter_by_date(start_date, end_date, order_book_ids, data)
                data = self.get_price_validate_fields(fields, data)

                # 使用 yield from 将数据添加到列表中
                yield from [data]

            # 关闭数据库连接
            db_session.close()
        else:  # 如果不需要分批次处理数据
            # 分批将dolphindb获取的数据转换成dataframe
            data = self._get_price_get_data_todf(total_data)

            ''' 数据处理 '''
            # 根据frequency进行处理
            data = self.get_price_by_type_frequency(asset_type, frequency, data)

            # 根据start_date和end_date筛选数据
            data = self.get_price_filter_by_date(start_date, end_date, order_book_ids, data)

            # 对fields进行处理
            data = self.get_price_validate_fields(fields, data)

            yield data

            # 关闭数据库连接
            db_session.close()

    # @staticmethod
    def get_price_validate_order_book_ids(self, order_book_ids):
        """
        对order_book_ids 类型 以及 是否必填 进行校验
        :param order_book_ids: 合约类型

        :return: None
        """
        self.general_validate_params_required(order_book_ids, "order_book_ids")  # 校验必填参数
        self.general_validate_field_str_or_list(order_book_ids, "order_book_ids")  # 校验参数类型

    def get_price_validate_frequency(self, frequency):
        """
        对frequency进行校验

        :param frequency: 频率
        :return: None
        """

        self.general_validate_params_required(frequency, "frequency")  # 校验必填参数
        if not isinstance(frequency, str):
            raise ValueError("frequency should be a string")

    def get_price_validate_start_end_date(self, start_date, end_date):
        """
        对 start_date 和 end_date 进行校验
        校验 start_date 和 end_date 是否同时提供，或者都不提供。

        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: None
        """
        if (start_date and not end_date) or (not start_date and end_date):
            raise ValueError("start_date and end_date should be both provided or not provided at all")
        if start_date and end_date:
            self.format_date(start_date)
            self.format_date(end_date)
            # 如果提供了，则进行进一步校验
            # is_start_datetime = self._is_convertible_datetime(start_date)
            # is_end_datetime = self._is_convertible_datetime(end_date)
            # if not is_end_datetime or not is_start_datetime:
            #     raise ValueError(
            #         "start_date and end_date should be datetime.datetime objects or "
            #         "convertible to datetime.datetime objects")
            #
            # # 如果传入的数据类型符合要求，进行转换
            # start_date, end_date = self._get_price_convert_start_end_date(start_date, end_date)
            # if start_date > end_date:
            #     raise ValueError("start_date should be earlier than end_date")

    @staticmethod
    def _get_price_convert_start_end_date(start_date, end_date):
        """
        将 start_date 和 end_date 转换为 datetime 类型。

        :param start_date: 开始日期，可以是 datetime.datetime 对象或字符串。
        :param end_date: 结束日期，可以是 datetime.datetime 对象或字符串。
        :return: 转换后的 start_date 和 end_date。
        """

        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S') if isinstance(start_date, str) \
            else start_date
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S') if isinstance(end_date, str) \
            else end_date

        return start_date, end_date

    @staticmethod
    def _is_convertible_datetime(date_data):
        """
        判断 date_data 是否是 datetime 类型或可以转换成 datetime 类型的字符串，并精确到秒。
        param: date_data: 要判断的值。

        Returns:
            True 如果 start_date 是 datetime 类型或可以转换成 datetime 类型的字符串，否则 False。
        """

        if isinstance(date_data, datetime.datetime):
            return True
        elif isinstance(date_data, str):
            try:
                datetime.datetime.strptime(date_data, "%Y-%m-%d %H:%M:%S")
                return True
            except ValueError:
                return False
        else:
            return False

    @staticmethod
    def get_price_filter_by_date(start_date, end_date, order_book_ids, data):
        """
        根据start_date和end_date筛选数据
        此处order_book_ids参数用于处理未传递start_date和end_date的情况(根据order_book_ids返回距离当前时间最近的一条数据)

        :param start_date: 开始时间
        :param end_date: 结束时间
        :param order_book_ids: 合约代码
        :param data: 数据
        :return: 处理后的数据
        """
        # 将'date_time'列转换为datetime类型
        try:
            if data['datetime'].dtype != 'datetime64[ns]':
                data['datetime'] = pd.to_datetime(data['datetime'])
        except ValueError:
            raise ValueError("source data's datetime format is not correct")

        # 如果传递了start_date 和 end_date, 则返回时间段内的数据
        if start_date and end_date:
            data = data[
                (data['datetime'] >= start_date) & (data['datetime'] <= end_date)]

        # 如果没有传递start_date 和 end_date, 则根据传入的order_book_ids返回每个合约距离当前时间最近的一条数据
        elif not start_date and not end_date:
            date_time = datetime.datetime.now()
            data = data[
                data["datetime"] <= date_time]

            # 根据传入的order_book_ids进行处理
            if isinstance(order_book_ids, str):
                data = data.tail(1)
            else:
                # 将order_book_id作为分组键，并找到每个分组中距离当前时间最近的数据
                nearest_data = data.groupby('order_book_ids')
                # 使用 tail(1) 获取每个组的最后一条数据
                data = nearest_data.apply(lambda x: x.tail(1)).reset_index(drop=True)

        return data

    def get_price_validate_fields(self, fields, data):
        """
        根据用户选择的字段返回数据
        :param fields: 字段列表 -- 用户传入的需要返回的字段
        :param data: 数据 -- 需要筛选的数据

        :return : data -- 返回筛选后的数据

        """
        # 此操作用于专门处理 1min_gtja 数据(因为该表的数据结构和其他表不一致)
        if fields:
            data = self.get_price_handle_1min_gtja(data, fields)

        data = self.general_validate_fields(data, fields)

        return data

    @staticmethod
    def get_price_handle_1min_gtja(data, fields):
        """
        处理1min_gtja数据
        如果是 1min_gtja 数据，字段和其他分钟k不一样，需要单独处理

        :param data: 需要处理的数据
        :param fields: 需要返回的字段
        :return:
        """

        new_df = data.copy()

        # 根据 unique_instrument_id 去交易参数表中获取缺失的数据
        # new_df['exchange_id'] =

        data_columns = data.columns.tolist()

        # 如果有字段在 1min_gtja 表中不存在, 则将该字段添加在结果中并设置为空
        for field in fields:
            if field not in data_columns:
                new_df[field] = None

        return new_df

    def get_price_by_type_frequency(self, asset_type, frequency, data):
        """
        根据合约类型和frequency筛选数据

        :param asset_type: 合约类型
        :param frequency: 频率
        :param data: 数据
        :return: data: 返回筛选后的数据
        """
        # 判断asset_type是否存在
        if not get_price_frequency_dict.get(asset_type, None):
            raise ValueError(
                f"asset_type: got invalided value {asset_type}, choose any in {list(get_price_frequency_dict.keys())}")

        # frequency是否存在
        exists, suffix = self._ends_with(frequency, list(get_price_frequency_dict[asset_type].keys()))
        if not exists:
            raise ValueError(f"{frequency} is not a valid frequency for {asset_type} contract")
        # frequency存在再根据频率对数据做进一步处理
        else:
            bar_or_tick = get_price_frequency_dict[asset_type][suffix]  # 获取数据类型是bar还是tick，根据值处理字段
            data = self.get_price_data_rename_columns(bar_or_tick, data)  # 重命名字段

        return data

    @staticmethod
    def _ends_with(variable, suffixes):
        """判断变量是否以列表中的元素结尾。
        :param variable: 待判断的变量
        :param suffixes: 列表，元素为字符串，表示后缀
        :return: True or False
        """
        for suffix in suffixes:
            if variable.endswith(suffix):
                return True, suffix
        return False, ""

    @staticmethod
    def get_price_data_rename_columns(bar_or_tick, data):
        """
        将从数据库中获取的数据列名重命名

        :param bar_or_tick: 是bar类型数据还是tick类型(不同类型字段不同)
        :param data: 数据
        :return: 处理后的数据
        """

        new_columns = get_price_data_type_dict.get(bar_or_tick)

        data = data.rename(columns=new_columns)
        return data

    def _get_price_get_data(self, order_book_ids, table_name, db_path, start_date, end_date):
        """
        用于接收数据表以及数据库，获取数据
        : params order_book_ids: 合约代码
        : params table_name: 数据表路径
        : params db_path: 数据库路径
        : params start_date: 开始时间
        : params end_date: 结束时间

        : return filtered_data: 从数据库获取并根据合约代码筛选后的数据
        """

        get_price_data, db_session = self.connect_db(table_name, db_path)

        # 使用 DolphinDB 的 where 子句筛选数据
        if isinstance(order_book_ids, str):
            limit_data = get_price_data.where(f"instrument_id='{order_book_ids}'")
        else:
            limit_data = get_price_data.where(f"instrument_id in {order_book_ids}")

        # 将日期转换成 DolphinDB 识别的日期格式，用于筛选数据
        # format_start_date = self.get_price_format_date(start_date)
        # format_end_date = self.get_price_format_date(end_date)
        format_start_date = self.format_date(start_date)
        format_end_date = self.format_date(end_date)

        # 根据日期对数据再次进行筛选，最大程度减轻数据库压力
        limit_data = limit_data.where(f"trade_time >= {format_start_date} and trade_time <= {format_end_date}")

        return limit_data, db_session

    @staticmethod
    def get_price_format_date(date_str):
        """将日期字符串格式化为 'YYYY.MM.DD HH:mm:ss' 格式。
        : params date_str: 日期字符串，例如 '2018-01-04 09:01:00'。
        : return ：
            格式化后的日期字符串，例如 '2018.01.04 09:01:00'。
        """
        if isinstance(date_str, str):
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            return date_obj.strftime('%Y.%m.%d %H:%M:%S')
        return date_str.strftime('%Y.%m.%d %H:%M:%S')

    @staticmethod
    def _get_price_get_data_todf(data):
        """
        用于接收从数据库获取的数据，并分批处理，将其转换成dataframe格式的数据返回
        : params data: 从数据库获取的数据
        : return : 转换成dataframe格式后的数据
        """

        result = pd.DataFrame()
        if data.rows > 1000000:
            chunk_size, start = 1000000, 0
            while start < data.rows:
                limit_data = data.limit([start, chunk_size]).toDF()
                result = limit_data if result.empty else pd.concat([result, limit_data], ignore_index=True)
                start += chunk_size

            return result
        return data.toDF()

    def get_price_data_get_data(self, order_book_ids, db_table_name, start_date, end_date):
        """
        根据参数获取数据库和表名，调用接口获取数据

        :param order_book_ids: 合约代码列表
        :param db_table_name: 数据库名称和表名
        :param start_date: 开始时间
        :param end_date: 结束时间
        :return: dolphin_data, db_session
        """

        dolphin_data, db_session = self._get_price_get_data(order_book_ids, *db_table_name, start_date, end_date)
        return dolphin_data, db_session

    @staticmethod
    def get_price_get_db_table_name(asset_type, frequency):
        if asset_type == "future":
            return {
                "tick_l1": (history_future_tick_db_table_name, history_future_tick_db_path),
                "1d": (history_future_day_db_table_name, history_future_day_db_path),
                "1min": (history_future_min_db_table_name, history_future_min_db_path),
                "1min_gtja": (history_future_1min_gtja_db_table_name, history_future_1min_gtja_db_path),
                "tick_l2": (history_future_tick_l2_db_table_name, history_future_tick_l2_db_path),
            }.get(frequency)
        elif asset_type == "option":
            return {
                "1d": (history_option_day_db_table_name, history_option_day_db_path),
                "1min": (history_option_min_db_table_name, history_option_min_db_path),
                "tick": (history_option_tick_db_table_name, history_option_tick_db_path),
            }.get(frequency)
        else:
            raise Exception("asset_type is not valid or frequency is not valid for this asset_type")

    """ get_instruments(合约基础信息) """

    def get_instruments(self, order_book_ids=None, commodity=None, asset_type=None, fields=None):
        """
        获取合约基础信息接口
        :param order_book_ids: str or list,合约代码 和 commodity_type 必填 二选一
        :param commodity: str or list, 合约品种  和 commodity_type 必填 二选一  若填写品种参数，则返回该品种所有合约基础信息
        :param asset_type: str, 合约类型--必填
        :param fields: str or list, 字段列表--选填，默认为全部字段
        :return: data:合约基础信息
        """

        ''' 数据校验 '''
        # 对order_book_ids和commodity是否必填进行校验
        self.get_instruments_validate_order_book_ids_commodity(order_book_ids, commodity)

        # 对asset_type进行校验
        self.general_validate_asset_type(asset_type)

        ''' 根据传入的asset_type以及order_book_ids获取数据 '''

        # 获取交易参数数据
        # 获取交易参数（根据交易参数的品种等信息处理后，再去期货/期权基础信息表获取对应信息）
        data = self.get_instruments_data_get_data(asset_type=asset_type, order_book_ids=order_book_ids,
                                                  commodity=commodity)
        # 重命名字段
        data = self.get_instruments_data_rename_columns(asset_type, data)

        # 从交易参数中填充commodity和trading_hour的值
        data = self.get_instruments_deal_commodity_trading_hour(data)

        ''' 按照文档筛选需要返回的字段 '''
        data = self.get_instruments_data_filter_return_fileds(asset_type, data)

        # 对fields进行校验并根据fields返回对应的字段
        data = self.get_instruments_validate_fields(fields, data)

        return data

    def get_instruments_validate_order_book_ids_commodity(self, order_book_ids, commodity):
        """
        对order_book_ids和commodity_type进行校验
        order_book_ids和commodity_type二选一，且只能二选一
        :param order_book_ids: str or list,合约代码
        :param commodity: str or list, 合约品种
        :return: None
        """

        ''' 对order_book_ids和commodity_type进行校验 '''
        self.general_validate_either_or("order_book_ids", order_book_ids, "commodity", commodity)

        if order_book_ids:
            self.general_validate_field_str_or_list(order_book_ids, "order_book_ids")
        if commodity:
            self.general_validate_field_str_or_list(commodity, "commodity")

    @staticmethod
    def get_instruments_data_filter_return_fileds(asset_type, data):
        """
        根据asset_type返回对应的字段(不同合约类型字段不同)
        :param asset_type: 合约类型，"future" or "option"
        :param data: 数据
        :return: data: 返回筛选后的数据
        """

        if asset_type == "future":
            data = data[get_instruments_type_dict.get("future_return_fields")]
        elif asset_type == "option":
            data = data[get_instruments_type_dict.get("option_return_fields")]

        return data

    def get_instruments_validate_fields(self, fields, data):
        """
        根据用户选择的字段返回数据
        :param fields: str or list, 字段列表
        :param data: 数据
        :return: data: 返回筛选后的数据
        """

        data = self.general_validate_fields(data, fields)

        return data

    def _get_instruments_data_get_data(self, order_book_ids, table_name, db_path):
        """
        用于接收数据表以及数据库，获取数据

        :param order_book_ids: 合约代码
        :param table_name: 数据表路径
        :param db_path: 数据库路径
        :return: 获取的数据
        """
        get_instruments_data, db_session = self.connect_db(table_name, db_path)

        filtered_data = pd.DataFrame()
        # 使用 DolphinDB 的 where 子句筛选数据
        if isinstance(order_book_ids, str):
            # filtered_data = get_instruments_data.where(f"mk_instrument_id='{order_book_ids}'").toDF() # qc_future_tradeparam
            filtered_data = get_instruments_data.where(f"instrument_id='{order_book_ids}'").toDF()  # qc_nexttradeparam
            # filtered_data = get_instruments_data.where(f"instrumentid='{order_book_ids}'").toDF()
        elif isinstance(order_book_ids, list):
            # filtered_data = get_instruments_data.where(f"mk_instrument_id in {order_book_ids}").toDF() # qc_future_tradeparam
            filtered_data = get_instruments_data.where(f"instrument_id in {order_book_ids}").toDF()  # qc_nexttradeparam
            # filtered_data = get_instruments_data.where(f"instrumentid in {order_book_ids}").toDF()

        # 关闭数据库连接
        db_session.close()

        return filtered_data

    # def get_instruments_data_get_data(self, asset_type=None, order_book_ids=None, commodity=None,
    #                                   trading_param_data=None):
    #     """
    #     qc_future_tradeparam
    #     根据参数获取数据库和表名，调用接口获取数据
    #
    #     :param asset_type: 合约类型
    #     :param order_book_ids: 合约代码
    #     :param commodity: 合约品种
    #     :param trading_param_data: 交易参数数据
    #     :return: data: 获取的数据
    #     """
    #
    #     # 如果传入的是commodity，需要获取参数品种下所有合约代码
    #     if commodity:
    #         # 如果传递的是品种信息，根据品种去交易参数表中查找出对对应的数据
    #         # 获取交易参数
    #         trading_param_data, db_session = self.connect_db(trading_params_db_table_name, trading_params_db_path)
    #         trade_df = trading_param_data.select("mk_instrument_id").toDF()
    #         trade_df["commodity"] = trade_df["mk_instrument_id"].apply(lambda x: re.match(r'^[A-Za-z]+', x).group(0))
    #
    #         if isinstance(commodity, str):
    #             order_book_ids = trade_df[trade_df['commodity'] == commodity]["mk_instrument_id"].to_list()
    #         else:
    #             order_book_ids = list(
    #                 set(trade_df[trade_df['commodity'].isin(commodity)]["mk_instrument_id"].to_list()))
    #
    #         # 关闭数据库连接
    #         db_session.close()
    #
    #     # 期货合约信息
    #     if asset_type == "future":
    #         data = self._get_instruments_data_get_data(order_book_ids,
    #                                                    future_contract_db_table_name,
    #                                                    future_contract_db_path)
    #         data["type"] = "future"
    #     # 期权合约信息
    #     elif asset_type == "option":
    #         data = self._get_instruments_data_get_data(order_book_ids,
    #                                                    option_contract_db_table_name,
    #                                                    option_contract_db_path)
    #         data["type"] = "option"
    #         data["exercise_type"] = data["optionstype"]
    #     else:
    #         raise Exception("asset_type is not valid")
    #
    #     data["commodity"] = ""
    #     data["trading_hour"] = ""
    #
    #     return data

    def get_instruments_data_get_data(self, asset_type=None, order_book_ids=None, commodity=None,
                                      ):
        """
        qc_nexttradeparam
        根据参数获取数据库和表名，调用接口获取数据

        :param asset_type: 合约类型
        :param order_book_ids: 合约代码
        :param commodity: 合约品种
        :return: data: 获取的数据
        """

        # 如果传入的是commodity，需要获取参数品种下所有合约代码
        if commodity:
            # 如果传递的是品种信息，根据品种去交易参数表中查找出对对应的数据
            # # 获取交易参数
            trading_param_data, db_session = self.connect_db(trading_params_db_table_name, trading_params_db_path)

            if isinstance(commodity, str):
                order_book_ids = list(set(
                    trading_param_data.select("instrument_id").where(f"product_id = '{commodity}'").toDF()[
                        "instrument_id"].to_list()))

            elif isinstance(commodity, list):
                order_book_ids = list(set(
                    trading_param_data.select("instrument_id").where(f"product_id in {commodity}").toDF()[
                        "instrument_id"].to_list()))

            # 关闭数据库连接
            db_session.close()

        # 期货合约信息
        if asset_type == "future":
            data = self._get_instruments_data_get_data(order_book_ids,
                                                       future_contract_db_table_name,
                                                       future_contract_db_path)
            data["type"] = "future"
        # 期权合约信息
        elif asset_type == "option":
            data = self._get_instruments_data_get_data(order_book_ids,
                                                       option_contract_db_table_name,
                                                       option_contract_db_path)
            data["type"] = "option"
            data["exercise_type"] = data["optionstype"]
        else:
            raise Exception("asset_type is not valid")
        data["commodity"] = ""
        data["trading_hour"] = ""

        return data

    @staticmethod
    def get_instruments_data_rename_columns(asset_type, data):
        """
        将从数据库中获取的数据列名重命名为文档要求的名字

        :param asset_type: 合约类型
        :param data: 数据
        :return: data
        """

        new_columns = get_instruments_type_dict.get(asset_type)
        data = data.rename(columns=new_columns)

        return data

    # @staticmethod
    # def get_instruments_deal_commodity_trading_hour(data):
    #     """
    #     qc_future_tradeparam
    #     用于处理commodity和trading_hour
    #     :param data: 数据
    #     :return: data: 处理后的数据
    #     """
    #
    #     try:
    #         # 最新的表中，品种直接从 mk_instument_id 截取
    #         data['commodity'] = data["order_book_id"].apply(lambda x: re.match(r'^[A-Za-z]+', x).group(0))
    #
    #         # 暂无trade_section，先不管
    #         # data.loc['trading_hour'] = data['trade_section'].iloc[0]
    #     except ValueError as e:
    #         print(e)
    #
    #     return data

    def get_instruments_deal_commodity_trading_hour(self, data):
        """
        qc_nexttradeparam
        用于处理commodity和trading_hour
        :param data: 数据
        :return: data: 处理后的数据
        """

        try:
            # 获取交易参数
            trading_param_data, db_session = self.connect_db(trading_params_db_table_name, trading_params_db_path)
            for index, row in data.iterrows():
                match = trading_param_data.toDF()[trading_param_data.toDF()['instrument_id'] == row['order_book_id']]
                # match = trading_param_data.toDF()[trading_param_data.toDF()['contractcode'] == row['order_book_id']]

                if not match.empty:
                    # data.loc[index, 'commodity'] = match['productcode'].iloc[0]
                    # data.loc[index, 'trading_hour'] = match['tradesection'].iloc[0]
                    data.loc[index, 'commodity'] = match['product_id'].iloc[0]
                    data.loc[index, 'trading_hour'] = match['trade_section'].iloc[0]
            db_session.close()
        except ValueError as e:
            print(e)

        return data

    """   get_trading_dates(交易日历)  """

    def get_trading_dates(self, date=datetime.date.today(), n=None, start_date=None, end_date=None,
                          is_include_start=True, is_include_end=True,
                          trade_time=None, date_count=None, date_type=None):
        """

        获取交易日历接口
        :param date: str--选填, 日期
        :param n: str--必填，根据不同值获取对应的交易日历
        :param start_date: str（datetime.date, datetime.datetime）--选填, 开始日期
        :param end_date: str（datetime.date, datetime.datetime）--选填, 结束日期
        :param is_include_start 是否包含开始日期
        :param is_include_end 是否包含结束日期
        若填写【date、n】为入参，则无法填写【start_date、end_date】，反之依然
        :return: data:交易日历

        当入参为trade_time, date_count, date_type时，功能如下：
        查询前后 N 个交易日或时间点
        :param trade_time: 当前时间点，格式为 'YYYY.MM.DD hh:mm:ss'
        :param date_count: 查询的交易日或时间数量，负数表示向前查询，正数表示向后查询
        :param date_type: 数据类型，'1d' 表示日频率，'1m' 表示分钟频率
        :return: 查询到的交易日或时间点列表
        """

        """ 校验参数 """
        if start_date and end_date:
            if not self.validate_dates(start_date, end_date):
                return None

        data = self.get_trading_dates_validate_date_n_start_end(date, n, start_date, end_date, is_include_start,
                                                                is_include_end, trade_time, date_count, date_type)

        return data

    def get_trading_dates_validate_date_n_start_end(self, date, n, start_date, end_date, is_include_start,
                                                    is_include_end, trade_time, date_count, date_type):
        """
        校验date、n和start_date、end_date有效性

        :param date: str-- 日期
        :param n: str--根据不同值获取对应的交易日历
        :param start_date: str（datetime.date, datetime.datetime）--开始日期
        :param end_date: str（datetime.date, datetime.datetime）--结束日期
        :param is_include_start 是否包含开始日期
        :param is_include_end 是否包含结束日期
        :param trade_time: 当前时间点，格式为 'YYYY.MM.DD hh:mm:ss'
        :param date_count: 查询的交易日或时间数量，负数表示向前查询，正数表示向后查询
        :param date_type: 数据类型，'1d' 表示日频率，'1m' 表示分钟频率
        :return: 如果校验通过，就返回对应的数据，否则抛出异常
        """

        if (date and n) and (start_date and end_date):
            raise ValueError("date、n and start_date、end_date can only be selected one at a time")
        if n and (start_date or end_date):
            raise ValueError("parameter error: cannot pass date、n and start_date、end_date at the same time")
        elif date and n:  # 根据date和n获取交易日历
            return self.get_trading_dates_by_date_n(date, n)
        elif start_date and end_date:  # 根据start_date和end_date获取交易日历
            return self.get_trading_dates_by_start_end(start_date, end_date, is_include_start, is_include_end)
        elif trade_time and date_count is not None and date_type:  # 查询前/后 N个交易日/时间数据
            return self.get_trading_date(trade_time, date_count, date_type)
        else:
            raise ValueError("parameter error: please pass date、n or start_date、end_date")

    def get_trading_dates_by_date_n(self, date, n):
        """
        校验 date 和 n
        :param date: str--选填, 日期
        :param n: str--必填，根据不同值获取对应的交易日历
        :return: 根据date和n筛选后的数据
        """

        if not isinstance(n, str):
            raise ValueError("n parameter error, type should be str")
        if n not in ["0", "1", "2", "3", "4", "5", "6"]:
            raise ValueError("n parameter error, value range should be [0, 1, 2, 3, 4, 5, 6]")
        if not isinstance(date, (str, datetime.date)):
            raise ValueError("date parameter error, type should be str or datetime.date")

        if isinstance(date, str):
            date = self.format_date_split_by_(date)
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

        return self.get_dates_in_n(date, n)

    def get_trading_dates_by_start_end(self, start_date, end_date, is_include_start, is_include_end):
        """
        根据start_date和end_date获取交易日历
        :param start_date: str（datetime.date, datetime.datetime）--选填, 开始日期
        :param end_date: str（datetime.date, datetime.datetime）--选填, 结束日期
        :param is_include_start 是否包含开始日期
        :param is_include_end 是否包含结束日期

        :return: data:根据start_date和end_date筛选后的数据
        """

        trading_params_data = self.get_trading_dates_get_data()

        # 动态生成比较运算符
        start_operator = operator.ge if is_include_start else operator.gt
        end_operator = operator.le if is_include_end else operator.lt

        # 校验日期类型
        if self.check_date_type(start_date, end_date):
            # 如果类型校验通过，则将start_date和end_date处理成对应的时间数据类型
            if isinstance(start_date, str):
                start_date = self._get_trading_dates_by_start_end(start_date)
            if isinstance(end_date, str):
                end_date = self._get_trading_dates_by_start_end(end_date)

            # 筛选 trading_day_str 列在 start_date 和 end_date 之间的数据
            # filtered_df = trading_params_data.loc[
            #     (trading_params_data['trading_day_str'] >= start_date) & (
            #             trading_params_data['trading_day_str'] <= end_date)]

            # 过滤数据
            filtered_df = trading_params_data.loc[
                start_operator(trading_params_data['trading_day_str'], start_date) &
                end_operator(trading_params_data['trading_day_str'], end_date)
                ]

            # 筛选 trade_flag 列等于 T 的数据（是交易日的数据）
            final_df = filtered_df.loc[filtered_df['trade_flag'] == 'T']
            date_list = sorted(final_df["trading_day_str"].tolist())
            formatted_date_list = [d.strftime('%Y.%m.%d') for d in date_list]

            return formatted_date_list
        else:
            raise ValueError(
                "start_date or end_date type error, please input str, datetime.date or datetime.datetime type")

    @staticmethod
    def _get_trading_dates_by_start_end(time_data):
        """
        将时间str数据处理成对应的时间类型（例如：date类型的str，处理成datetime.date类型）

        :param time_data: 时间数据
        :return: 转换后的时间数据类型
        """

        if isinstance(time_data, str):
            time_data = time_data.replace('.', '-')

        try:
            time_data = datetime.datetime.strptime(time_data, "%Y-%m-%d").date()
            return time_data
        except ValueError:
            try:
                time_data = datetime.datetime.strptime(time_data, "%Y-%m-%d %H:%M:%S").date()
                return time_data
            except ValueError:
                raise ValueError("parameter type error")

    def check_date_type(self, _start_date, _end_date):
        """
        判断start_date和end_date是否为str，datetime.date, datetime.datetime三种类型，
        其中，如果是str类型，还要判断是否是datetime.date, datetime.datetime两种类型的字符串.
        :params _start_date: 开始日期
        :params _end_date: 结束日期

        :return: 如果类型正确，返回 True。否则返回 False，并打印错误信息
        """

        if isinstance(_start_date, str):
            _start_date = _start_date.replace('.', '-')
        if isinstance(_start_date, str):
            _end_date = _end_date.replace('.', '-')

        if isinstance(_start_date, (str, datetime.date, datetime.datetime)) and \
                isinstance(_end_date, (str, datetime.date, datetime.datetime)):
            if isinstance(_start_date, str) and not self.general_validate_date(_start_date):
                raise ValueError("start_date is not a valid date string format")
            if isinstance(_end_date, str) and not self.general_validate_date(_end_date):
                raise ValueError("end_date is not a valid date string format")
            return True
        else:
            raise ValueError(
                "start_date or end_date type error, please input str, datetime.date or datetime.datetime type")

    def get_trading_dates_get_data(self):
        """
        从dolphindb获取交易日历
        :return: 交易日历数据
        """

        params_data, db_session = self.connect_db(trading_dates_db_table_name, trading_dates_db_path)
        trading_params_data = params_data.toDF()
        trading_params_data["trading_day_str"] = pd.to_datetime(trading_params_data["trading_day_str"],
                                                                format="%Y%m%d").dt.date
        db_session.close()
        return trading_params_data

    @staticmethod
    def get_date_get_week_month_year(data, start_date, end_date):
        """
        用于获取当前日期所在周、月、年的交易日数据

        :param data: 交易日历数据
        :param start_date: 开始日期
        :param end_date: 结束日期

        :return: 交易日历数据

        """

        # 获取开始日期和结束日期
        start_date = datetime.datetime.strptime(start_date, "%Y%m%d").date()
        end_date = datetime.datetime.strptime(end_date, "%Y%m%d").date()

        # 筛选出时间段内的所有数据
        filtered_df = data.loc[(data['trading_day_str'] >= start_date) & (data['trading_day_str'] <= end_date)]
        # 筛选出时间段内的所有交易日
        final_df = filtered_df.loc[filtered_df['trade_flag'] == 'T']

        return sorted(final_df["trading_day_str"].tolist())

    def get_dates_in_n(self, _date, _n):
        """
        获取选定日期, 根据n值获取对应的交易日历。

        :param _date: 选定的日期，可以是 datetime.date 或 datetime.datetime 对象
        :param _n: 时间段，可以是 'week'、'month' 或 'year'
        :return: 一个包含所有日期的列表
        """

        trading_params_data = self.get_trading_dates_get_data()

        cn_holidays = holidays.CN()  # 创建中国节假日对象

        time_period_mapping_dict = {
            "0": _date in cn_holidays,
            "1": trading_params_data.loc[trading_params_data["trading_day_str"] == _date]["next_trading_day"].iloc[0],
            "2": trading_params_data.loc[trading_params_data["trading_day_str"] == _date]["pre_trading_day"].iloc[0],
            "3": self.get_date_get_week_month_year(trading_params_data,
                                                   trading_params_data.loc[
                                                       trading_params_data["trading_day_str"] == _date][
                                                       "first_trading_day_week"].iloc[0],
                                                   trading_params_data.loc[
                                                       trading_params_data["trading_day_str"] == _date][
                                                       "last_trading_day_week"].iloc[0]),
            "4": self.get_date_get_week_month_year(trading_params_data,
                                                   trading_params_data.loc[
                                                       trading_params_data["trading_day_str"] == _date][
                                                       "first_trading_day_month"].iloc[0],
                                                   trading_params_data.loc[
                                                       trading_params_data["trading_day_str"] == _date][
                                                       "last_trading_day_month"].iloc[0]),
            "5": self.get_date_get_week_month_year(trading_params_data,
                                                   trading_params_data.loc[
                                                       trading_params_data["trading_day_str"] == _date][
                                                       "first_trading_day_year"].iloc[0],
                                                   trading_params_data.loc[
                                                       trading_params_data["trading_day_str"] == _date][
                                                       "last_trading_day_year"].iloc[0]),
            "6": trading_params_data.loc[trading_params_data["trading_day_str"] == _date]["night_day"].iloc[0],
        }

        if _n not in time_period_mapping_dict:
            raise ValueError("n parameter error, value range should be [0, 1, 2, 3, 4, 5, 6]")

        return time_period_mapping_dict[_n]

    """ get_margin_ratio 期货保证金 """

    def get_margin_ratio(self, order_book_id=None, commodity=None, date=datetime.datetime.now(), exchange=None):
        """
        获取期货保证金信息接口
        :param order_book_id: str--选填（和commodity二选一），合约代码
        :param commodity: str--选填（和order_book_id二选一），合约品种,如果入参为品种，则返回该品种条件下所有合约的保证金list
        :param date: datetime--必填（默认今天)，日期
        :param exchange: str--必填，交易所
        :return: 期货保证金数据
        """

        """ 校验数据 """
        self.get_margin_ratio_validate_params(order_book_id, commodity, date, exchange)

        """ 获取数据 """
        ''' 根据order_book_ids和commodity_type进行筛选 '''
        data, db_session = self.get_margin_ratio_get_data(order_book_id, commodity, date, exchange)
        db_session.close()

        """ 处理数据 """
        data = self.get_margin_ration_handle_data(data)

        return data

    def get_margin_ratio_validate_params(self, order_book_id, commodity, date, exchange):
        """
        校验参数
        :param order_book_id: 合约代码
        :param commodity: 合约品种
        :param date: 日期
        :param exchange: 交易所
        :return:
        """

        # 校验order_book_id和commodity
        self.get_margin_ratio_validate_order_book_id_commodity(order_book_id, commodity)

        # 校验exchange
        self.get_margin_ratio_validate_exchange(exchange)

        # 校验date
        self.get_margin_ratio_validate_date(date)

    def get_margin_ratio_validate_exchange(self, exchange):
        """
        校验exchange
        :param exchange: str--必填，交易所
        :return: None
        """

        self.general_validate_params_required(exchange, "exchange")  # 校验必填参数

        if not isinstance(exchange, str):
            raise ValueError("exchange should be str")

    def get_margin_ratio_validate_order_book_id_commodity(self, order_book_id, commodity):
        """
        校验order_book_id和commodity
        :param order_book_id: str--二选一，合约代码
        :param commodity: str--二选一，品种
        :return: data: 期货保证金数据
        """

        ''' 对order_book_ids和commodity_type进行校验 '''
        self.general_validate_either_or("order_book_id", order_book_id, "commodity", commodity)

    def get_margin_ratio_get_data(self, order_book_id, commodity, date, exchange):
        """
        获取数据
        :param order_book_id: str--二选一，合约代码
        :param commodity: str--二选一，品种
        :param date: str--必填，日期
        :param exchange: str--必填，交易所
        :return: data: 期货保证金数据
        """

        # 从数据库中获取数据 (因为目前需求中所需的字段在交易参数表中都已存在，所以直接从交易参数表中获取)
        # data, db_session = self.connect_db(margin_db_table_name, margin_db_path)  # 期货保证金表
        data, db_session = self.connect_db(trading_params_db_table_name, trading_params_db_path)  # 交易参数表

        # 根据 date 筛选数据
        # 将日期转换成 DolphinDB 识别的日期格式，用于筛选数据
        # dolphin_date = self.get_margin_ratio_date_to_dolphin_time(date)
        dolphin_date = self.format_date(date)
        date_data = data.where(f"trading_day = {dolphin_date}")

        # 根据 exchange 筛选数据
        # 目前没有交易所字段
        exchange_data = date_data.where(f"exchange_id = '{exchange}'")

        # 根据 order_book_id 和 commodity 获取数据
        if order_book_id:  # 如果 order_book_id 不为空，则根据 order_book_id 获取数据
            get_margin_ratio_data = exchange_data.where(f"instrument_id in {order_book_id}") if isinstance(
                order_book_id,
                list) else \
                exchange_data.where(f"instrument_id = '{order_book_id}'").toDF()
        else:  # 如果 commodity 不为空，则根据 commodity 获取数据
            get_margin_ratio_data = exchange_data.where(f"product_id in {commodity}") if isinstance(
                commodity, list) else \
                exchange_data.where(f"product_id = '{commodity}'").toDF()

        return get_margin_ratio_data, db_session

    @staticmethod
    def get_margin_ration_handle_data(data):
        """
        处理返回结果
        :param data: 数据
        :return: 处理后的返回结果
        """

        new_df = data.copy()
        # 筛选出需求文档中指定的字段
        # (由于更换了新的交易参数表，文档要求的部分字段在新表中暂无，所以字典中暂时不取，后续如果更新后，更新对应字典即可)
        new_df = new_df[future_margin_ratio_return_fields]

        # 将实际数据字段转换成需求文档中指定的字段
        new_df.rename(columns=future_margin_ratio_return_fields_rename, inplace=True)

        return new_df

    def get_margin_ratio_date_to_dolphin_time(self, date):
        """
            将日期字符串格式化为 'YYYY.MM.DD HH:mm:ss' 格式。
            : params date: 日期字符串，例如 '2018-01-04 09:01:00'。
            : return ：
                格式化后的日期字符串，例如 '2018.01.04 09:01:00'。
        """
        if isinstance(date, str):
            date_obj = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S') if (
                self.general_validate_date_str_is_datetime_type(date)) else \
                datetime.datetime.strptime(date, '%Y-%m-%d')
            return date_obj.strftime('%Y.%m.%d %H:%M:%S')
        return date.strftime('%Y.%m.%d %H:%M:%S')

    @staticmethod
    def get_margin_ratio_re(instrument_id):
        # 提取开头字母的函数
        match = re.match(r'^[A-Za-z]+', instrument_id)
        return match.group(0) if match else ''

    def get_margin_ratio_validate_date(self, date):
        """
        校验date
        :param date: datetime--日期
        :return: None
        """

        self.format_date(date)

        # if isinstance(date, (str, datetime.date, datetime.datetime)):
        #     if isinstance(date, str) and not self.general_validate_date(date):
        #         raise ValueError("date is not a valid date string format")
        # else:
        #     raise ValueError("date type error, please pass in str, datetime.date or datetime.datetime type")

    """ get_fee 期货交割手续费 """

    def get_fee(self, order_book_id=None, commodity=None, date=datetime.datetime.now(), exchange=None):
        """
        获取期货交割手续费信息接口
        :param order_book_id: str--选填（和commodity二选一），合约代码
        :param commodity: str--选填（和order_book_id二选一），合约品种,如果入参为品种，则返回该品种条件下所有合约的交割手续费list
        :param date: datetime--必填（默认今天)，日期
        :param exchange: str--必填，交易所
        :return: 期货交割手续费
        """

        """ 校验参数 """
        self.get_fee_validate_params(order_book_id, commodity, date, exchange)

        """ 获取数据 """
        data, db_session = self.get_fee_get_data(order_book_id, commodity, date, exchange)
        db_session.close()

        """ 处理返回结果 """
        data = self.get_fee_handle_data(data)

        return data

    def get_fee_validate_params(self, order_book_id, commodity, date, exchange):
        """
        校验参数
        :param order_book_id:
        :param commodity:
        :param date:
        :param exchange:
        :return:
        """

        # 校验order_book_id和commodity
        self.get_fee_validate_order_book_id_commodity(order_book_id, commodity)

        # 校验exchange
        self.get_fee_validate_exchange(exchange)

        # 校验date
        self.get_fee_validate_date(date)

    def get_fee_validate_exchange(self, exchange):
        """
        校验exchange
        :param exchange: str--必填，交易所
        :return: None
        """
        # 是否必填
        self.general_validate_params_required(exchange, "exchange")

        if not isinstance(exchange, str):
            raise ValueError("exchange should be str")

    def get_fee_validate_order_book_id_commodity(self, order_book_id, commodity):
        """
        校验order_book_id和commodity
        :param order_book_id: str--二选一，合约代码
        :param commodity: str--二选一，品种
        :return:
        """

        ''' 对order_book_ids和commodity_type进行校验 (这两个参数只能填写其中之一) '''
        self.general_validate_either_or("order_book_id", order_book_id, "commodity", commodity)

        # 校验 order_book_id 和 commodity_type 参数类型
        if order_book_id:
            self.general_validate_field_str_or_list(order_book_id, "order_book_id")  # 校验参数类型
        else:
            self.general_validate_field_str_or_list(commodity, "commodity")  # 校验参数类型

    def get_fee_get_data(self, order_book_id, commodity, date, exchange):
        """
        获取期货交割手续费数据
        :param order_book_id: str--二选一，合约代码
        :param commodity: str--二选一，品种
        :param date: str--二选一，日期
        :param exchange: str--交易所
        :return: data:期货交割手续费数据
        """
        # 从数据库中获取数据 (因为目前需求中所需的字段在交易参数表中都已存在，所以直接从交易参数表中获取)
        # data, db_session = self.connect_db(delivery_fee_db_table_name, delivery_fee_db_path)  # 期货交割手续费表
        data, db_session = self.connect_db(trading_params_db_table_name, trading_params_db_path)

        # 根据 order_book_id 和 commodity 获取数据
        if order_book_id:  # 如果 order_book_id 不为空，则根据 order_book_id 获取数据
            get_fee_data = data.where(f"instrument_id in {order_book_id}") if isinstance(order_book_id, list) else \
                data.where(f"instrument_id = '{order_book_id}'")
        else:  # 如果 commodity 不为空，则根据 commodity 获取数据
            get_fee_data = data.where(f"product_id in {commodity}") if isinstance(commodity, list) else \
                data.where(f"product_id = '{commodity}'")

        # 根据 date 筛选数据
        # 将日期转换成 DolphinDB 识别的日期格式，用于筛选数据
        # dolphin_date = self.get_fee_datetime_to_dolphin_time(date)
        dolphin_date = self.format_date(date)

        date_data = get_fee_data.where(f"trading_day = {dolphin_date}")

        # 根据 exchange 筛选数据
        exchange_data = date_data.where(f"exchange_id = '{exchange}'")

        return exchange_data.toDF(), db_session

    def get_fee_datetime_to_dolphin_time(self, date):
        """
        将日期字符串格式化为 'YYYY.MM.DD HH:mm:ss' 格式。
        : params date: 日期字符串，例如 '2018-01-04 09:01:00'。
        : return ：
            格式化后的日期字符串，例如 '2018.01.04 09:01:00'。
        """
        if isinstance(date, str):
            date_obj = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S') if (
                self.general_validate_date_str_is_datetime_type(date)) else \
                datetime.datetime.strptime(date, '%Y-%m-%d')
            return date_obj.strftime('%Y.%m.%d %H:%M:%S')
        return date.strftime('%Y.%m.%d %H:%M:%S')

    def get_fee_validate_date(self, date):
        """
        校验date
        :param date: datetime--日期
        :return: None
        """
        # 校验参数是否必填
        self.general_validate_params_required(date, "date")

        self.format_date(date)

        # # 校验参数类型格式
        # if isinstance(date, (str, datetime.date, datetime.datetime)):
        #     if isinstance(date, str) and not self.general_validate_date(date):
        #         raise ValueError("date is not a valid date string format")
        # else:
        #     raise ValueError("date type error, please pass in str, datetime.date or datetime.datetime type")

    @staticmethod
    def get_fee_handle_data(data):
        """
        处理返回结果
        :param data: 数据
        :return: 处理后的返回结果
        """

        # 筛选出需求文档中指定的字段
        new_df = data.copy()
        new_df = new_df[future_delivery_fee_return_fields]

        # 将实际数据字段转换成需求文档中指定的字段
        new_df.rename(columns=future_delivery_fee_return_fields_rename, inplace=True)

        return new_df

    """ get_limit_position 期货限仓数据 """

    def get_limit_position(self, order_book_ids=None, commodity=None, date=datetime.date.today()):
        """
        获取期货限仓数据接口
        :param order_book_ids: str or list--选填（和commodity二选一），合约代码
        :param commodity: str or list--选填（和order_book_ids二选一），合约品种
        :param date: datetime.date--选填（默认今天)，日期
        :return: 期货限仓数据

        """

        """ 校验数据 """
        self.get_limit_position_validate_params(order_book_ids, commodity, date)

        """ 获取数据 """
        ''' 根据order_book_ids和commodity_type进行筛选 '''
        data, db_session = self.get_limit_position_get_data(order_book_ids, commodity, date)
        db_session.close()

        """ 处理结果 """
        data = self.get_limit_position_handle_data(data)

        return data

    def get_limit_position_validate_params(self, order_book_ids, commodity, date):
        """
        校验参数
        :param order_book_ids: 合约代码
        :param commodity: 品种
        :param date: 日期
        :return:
        """

        # 校验order_book_ids和commodity
        self.get_limit_position_validate_order_book_ids_commodity(order_book_ids, commodity)

        # 校验date
        self.get_limit_position_validate_date(date)

    def get_limit_position_validate_order_book_ids_commodity(self, order_book_ids, commodity):
        """
        对order_book_ids和commodity_type进行校验
        :param order_book_ids: str or list--选填（和commodity二选一），合约代码
        :param commodity: str or list--选填（和order_book_ids二选一），合约品种
        :return: data: 期货限仓数据
        """
        self.general_validate_either_or("order_book_ids", order_book_ids, "commodity", commodity)

    def get_limit_position_get_data(self, order_book_ids, commodity, date):
        """
        获取数据
        :param order_book_ids: 合约代码
        :param commodity: 品种
        :param date: 日期
        :return: 期货限仓数据
        """

        # 从数据库中获取数据 (因为目前需求中所需的字段在交易参数表中都已存在，所以直接从交易参数表中获取)
        # data, db_session = self.connect_db(limit_position_db_table_name, limit_position_db_path)  # 期货限仓数据
        data, db_session = self.connect_db(trading_params_db_table_name, trading_params_db_path)  # 交易参数表

        # 根据 date 筛选数据
        # 将日期转换成 DolphinDB 识别的日期格式，用于筛选数据
        # dolphin_date = self.get_limit_position_date_to_dolphin_time(date)
        dolphin_date = self.format_date(date)
        date_data = data.where(f"trading_day = {dolphin_date}")

        # 根据 order_book_id 和 commodity 获取数据
        if order_book_ids:  # 如果 order_book_id 不为空，则根据 order_book_id 获取数据
            get_limit_position_data = date_data.where(f"instrument_id in {order_book_ids}") if isinstance(
                order_book_ids,
                list) else \
                date_data.where(f"instrument_id = '{order_book_ids}'").toDF()
        else:  # 如果 commodity 不为空，则根据 commodity 获取数据
            get_limit_position_data = date_data.where(f"product_id in {commodity}") if isinstance(
                commodity, list) else \
                date_data.where(f"product_id = '{commodity}'").toDF()

        return get_limit_position_data, db_session

    def get_limit_position_date_to_dolphin_time(self, date):
        """
            将日期字符串格式化为 'YYYY.MM.DD HH:mm:ss' 格式。
            : params date: 日期字符串，例如 '2018-01-04 09:01:00'。
            : return ：
                格式化后的日期字符串，例如 '2018.01.04 09:01:00'。
        """
        if isinstance(date, str):
            date_obj = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S') if (
                self.general_validate_date_str_is_datetime_type(date)) else \
                datetime.datetime.strptime(date, '%Y-%m-%d')
            return date_obj.strftime('%Y.%m.%d %H:%M:%S')
        return date.strftime('%Y.%m.%d %H:%M:%S')

    def get_limit_position_validate_date(self, date):
        """
        校验date
        :param date: datetime.date--选填，日期
        :return: None
        """

        self.format_date(date)

        # if isinstance(date, (str, datetime.date, datetime.datetime)):
        #     if isinstance(date, str) and not self.general_validate_date(date):
        #         raise ValueError("date is not a valid date string format")
        # else:
        #     raise ValueError("date type error, please pass in str, datetime.date or datetime.datetime type")

    @staticmethod
    def get_limit_position_handle_data(data):
        """
        处理返回结果
        :param data: 数据
        :return: 处理后的返回结果
        """

        new_df = data.copy()
        # 筛选出需求文档中指定的字段
        # (由于更换了新的交易参数表，文档要求的部分字段在新表中暂无，所以字典中暂时不取，后续如果更新后，更新对应字典即可)
        new_df = new_df[future_limit_position_return_fields]

        # 将实际数据字段转换成需求文档中指定的字段
        new_df.rename(columns=future_limit_position_return_fields_rename, inplace=True)

        return new_df

    """ get_active_contract 主力/次主力合约 """

    def get_active_contract(self, commodity=None, start_date=datetime.date.today(),
                            end_date=datetime.date.today(), frequency=None, compute_type=None,
                            fields=None, adjust_type=None, adjust_method=None, source=None):
        """
        获取主力/次主力合约信息接口
        :param commodity: str or str list--必填，品种
        :param start_date: date--必填，默认当天
        :param end_date: date--必填，默认当天
        :param frequency: str--必填
        :param compute_type: str--必填，active指主力；next_active次主力
        :param fields: str or str list--选填，返回字段，默认全部
        :param adjust_type: str--选填，复权方式：不复权 - none，后复权 - post
        :param adjust_method: str--选填，复权方法
        :param source: str--选填，数据源，默认研究所, 3个来源可选：1-数据中台, 2-米筐, 3-研究所(表中无研究所的source)

        :return: 主力/次主力合约
        """

        """ 校验参数 """
        if start_date and end_date:
            if not self.validate_dates(start_date, end_date):
                return None

        self.get_active_contract_validate_params(commodity, start_date, end_date, frequency, compute_type, adjust_type,
                                                 adjust_method)

        """ 获取、筛选数据 """
        if frequency in ['1min', '1d', '1min_gtja']:
            data, db_session = self.get_active_contract_get_data(commodity, start_date, end_date, frequency,
                                                                 compute_type,
                                                                 source)
        else:
            data, db_session = self.get_active_contract_get_data_tick(commodity, start_date, end_date, frequency,
                                                                      compute_type,
                                                                      source)
            data = self.get_active_contract_tick_data(data, frequency, start_date, end_date)
        db_session.close()

        """ 处理字段名 """
        data = self.get_active_contract_rename(data, adjust_method, frequency)

        """ 根据是否复权计算价格数据 """
        data = self.get_active_contract_adjust_price(data, adjust_type, adjust_method, frequency)

        """ 处理返回字段 """
        data = self.get_active_contract_process_return_fields(data, fields)

        return data

    def get_active_contract_validate_params(self, code, start_date, end_date, frequency, asset_type, adjust_type,
                                            adjust_method):
        """
        校验参数
        Args:
            code: str or str list--选填，合约代码，默认全部
            start_date: str--选填，开始日期，默认全部
            end_date: str--选填，结束日期，默认全部
            frequency: str--必填
            asset_type: str--选填，合约类型，默认全部
            adjust_type: str--选填，复权类型
            adjust_method: str--选填，复权方法
        Raises:
            ValueError: 参数错误
        """

        # 校验必填参数
        self.get_active_contract_validate_required_params(code, start_date, end_date, frequency, asset_type)

        # 校验日期参数类型
        self.get_active_contract_validate_date_type(start_date, end_date)

        # 校验code类型
        self.get_active_contract_validate_code(code)

        # 校验 adjust_type, adjust_method
        self.general_validate_param_is_str("adjust_type", adjust_type)
        self.general_validate_param_is_str("adjust_method", adjust_method)

    def get_active_contract_validate_required_params(self, code, start_date, end_date, frequency, asset_type):
        """
        校验参数是否必填
        :param code: str or str list--必填，品种
        :param start_date: date--必填，默认当天
        :param end_date: date--必填，默认当天
        :param frequency: str--必填
        :param asset_type: str--必填，active指主力；next_active次主力
        :return: None
        """

        params_dict = {
            "code": code,
            "start_date": start_date,
            "end_date": end_date,
            "asset_type": asset_type,
            "frequency": frequency
        }
        for key, value in params_dict.items():
            self.general_validate_params_required(value, key)  # 校验必填参数

    def get_active_contract_validate_code(self, code):
        """
        校验code 类型
        :param code: str or str list--必填，品种
        :return: None
        """
        self.general_validate_field_str_or_list(code, "code")

    @staticmethod
    def get_active_contract_get_table(frequency):
        """
        获取表信息
        :param frequency: 频率
        :return: 表信息
        """

        return {
            '1d': (qc_future_maincontract_dayk, dayk_future_maincontract_db),
            '1min': (qc_future_maincontract_minutek, minutek_future_maincontract_db),
            '1min_gtja': (qc_future_maincontract_gtja_minutek, minutek_future_maincontract_gtja_db)
        }.get(frequency, (None, None))

    @staticmethod
    def get_active_contract_get_table_tick(frequency):
        """
        获取表信息
        :param frequency: 频率
        :return: 表信息
        """

        return {
            'tick_l1': (tick_main_contract_db_table_name, tick_main_contract_db_path),
            'tick_l2': (tick_main_contract_db_table_name, tick_main_contract_db_path),
        }.get(frequency, (None, None))

    def get_active_contract_get_data(self, code, start_date, end_date, frequency, compute_type, source):
        """
        获取数据
        :param code: str or str list--必填，品种
        :param start_date: str--必填，开始日期
        :param end_date: str--必填，结束日期
        :param compute_type: str--必填，资产类型
        :param frequency: str--必填
        :param source: str--选填，数据来源

        :return: 主力/次主力合约数据
        """

        # 根据频率获取对应的表
        table_name, db_path = self.get_active_contract_get_table(frequency)

        # 先从数据库获取数据
        data, db_session = self.connect_db(table_name, db_path)

        # 根据code筛选数据
        code_data = data.where(f"product_id in {code}") if isinstance(code, list) else \
            data.where(f"product_id = '{code}'")

        # 根据日期筛选数据
        # 将日期转换成 DolphinDB 识别的日期格式，用于筛选数据
        # start_dolphin_date = self.get_active_contract_datetime_to_dolphin_time(start_date)
        # end_dolphin_date = self.get_active_contract_datetime_to_dolphin_time(end_date)

        start_dolphin_date = self.format_date(start_date)
        end_dolphin_date = self.format_date(end_date)

        date_data = code_data.where(f"trading_day >= {start_dolphin_date} and trading_day <= {end_dolphin_date}")

        if compute_type:
            # 根据表中的 rank 字段筛选主力/次主力合约，rank == 1是主力合约， 2 是次主力合约
            rank = 'MAIN' if compute_type == "main" else 'SUB_MAIN'
            rank_data = date_data.where(f"compute_type = '{rank}'")

            return rank_data.toDF(), db_session
        return date_data.toDF(), db_session

    def get_active_contract_get_data_tick(self, code, start_date, end_date, frequency, compute_type, source):
        """
        获取tick数据
        :param code: str or str list--必填，品种
        :param start_date: str--必填，开始日期
        :param end_date: str--必填，结束日期
        :param compute_type: str--必填，资产类型
        :param frequency: str--必填
        :param source: str--选填，数据来源

        :return: 主力/次主力合约数据
        """

        table_name, db_path = main_contract_db_table_name, main_contract_db_path

        # 先从数据库获取数据
        data, db_session = self.connect_db(table_name, db_path)

        # 根据code筛选数据
        code_data = data.where(f"product_id in {code}") if isinstance(code, list) else \
            data.where(f"product_id = '{code}'")

        # 根据日期筛选数据
        # 将日期转换成 DolphinDB 识别的日期格式，用于筛选数据
        # start_dolphin_date = self.get_active_contract_datetime_to_dolphin_time(start_date)
        # end_dolphin_date = self.get_active_contract_datetime_to_dolphin_time(end_date)
        start_dolphin_date = self.format_date(start_date)
        end_dolphin_date = self.format_date(end_date)

        date_data = code_data.where(f"trading_day >= {start_dolphin_date} and trading_day <= {end_dolphin_date}")

        # 根据表中的 rank 字段筛选主力/次主力合约，rank == 1是主力合约， 2 是次主力合约
        if compute_type:
            rank = 'MAIN' if compute_type == "main" else 'SUB_MAIN'
            rank_data = date_data.where(f"compute_type = '{rank}'")
            return rank_data.toDF(), db_session

        return date_data.toDF(), db_session

    def get_active_contract_tick_data(self, data, frequency, start_date, end_date):
        """
        根据主力合约表查询tick表
        :param data: 数据
        :param frequency: 频率
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 查询后的数据
        """

        table_name, db_path = self.get_active_contract_get_table_tick(frequency)
        # 先从数据库获取数据
        tick_data, db_session = self.connect_db(table_name, db_path)

        # 根据日期筛选数据
        start_dolphin_date = self.format_date(start_date)
        end_dolphin_date = self.format_date(end_date)
        date_data = tick_data.where(f"trading_day >= {start_dolphin_date} and trading_day <= {end_dolphin_date}")

        instrument_data = date_data.where(f"instrument_id in {data['instrument_id'].tolist()}")

        fina_data = instrument_data.toDF()
        db_session.close()

        return fina_data

    @staticmethod
    def get_active_contract_datetime_to_dolphin_time(datetime_str):
        """将日期字符串格式化为 'YYYY.MM.DD HH:mm:ss' 格式。
                : params datetime_str: 日期字符串，例如 '2018-01-04 09:01:00'。
                : return ：
                    格式化后的日期字符串，例如 '2018.01.04 09:01:00'。
                """
        if isinstance(datetime_str, str):
            try:
                datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
                date_obj = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
                return date_obj.strftime('%Y.%m.%d %H:%M:%S')
            except ValueError:
                date_obj = datetime.datetime.strptime(datetime_str, '%Y-%m-%d')
                return date_obj.strftime('%Y.%m.%d')
        else:
            return datetime_str.strftime('%Y.%m.%d %H:%M:%S')

    def get_active_contract_validate_date_type(self, start_date, end_date):
        """
        校验日期数据的类型
        :param start_date: date--必填，默认当天
        :param end_date: date--必填，默认当天
        :return: None
        """
        # 校验start_date 和 end_date 是否为datetime.date类型或者可以转换成该类型的str
        # if isinstance(start_date, (str, datetime.date)) and isinstance(end_date, (str, datetime.date)):
        #     if isinstance(start_date, str) and not self.general_validate_date_str_is_date_type(start_date):
        #         raise ValueError("start_date type error， please enter datetime.date type")
        #     if isinstance(end_date, str) and not self.general_validate_date_str_is_date_type(end_date):
        #         raise ValueError("start_date type error， please enter datetime.date type")
        # else:
        #     raise ValueError("start_date or end_date type error, please enter datetime.date type")

        self.format_date(start_date)
        self.format_date(end_date)

        # 校验begin_date 是否为datetime.datetime类型或者为可以转换为该类型的字符串
        # if isinstance(begin_date, (str, datetime.datetime)):
        #     if isinstance(begin_date, str) and not self.general_validate_date_str_is_datetime_type(begin_date):
        #         raise ValueError("begin_date type error， please enter datetime.datetime type")
        # else:
        #     raise ValueError("begin_date type error， please enter datetime.datetime type")

    @staticmethod
    def get_active_contract_rename(data, ex_factor, frequency):
        """
        处理返回结果
        :param data: 数据
        :param ex_factor: 复权因子
        :param frequency: 频率
        :return: 处理后的返回结果
        """
        new_df = data.copy()

        if frequency in ['1min', '1d']:
            return_fields = main_contract_return_fields
            return_fields_rename = main_contract_return_fields_rename
        elif frequency in ['1min_gtja']:
            return_fields = gtja_mink_main_contract_return_fields
            return_fields_rename = gtja_mink_main_contract_return_fields_rename
        else:
            return_fields = tick_main_contract_return_fields
            return_fields_rename = tick_main_contract_return_fields_rename

        # 筛选出需求文档中指定的字段
        new_df = new_df[return_fields]

        # 将实际数据字段转换成需求文档中指定的字段
        new_df.rename(columns=return_fields_rename, inplace=True)

        if frequency in ['1min', '1d']:
            new_df['none_close'] = new_df['close']
            new_df['none_prev_close'] = new_df['prev_close']
            new_df['ex_factor'] = ex_factor
        elif frequency in ['1min_gtja']:
            new_df['ex_factor'] = ex_factor
        else:
            new_df['total_turnover'] = new_df.groupby(['order_book_ids', 'trading_day'])['turnover'].transform('sum')

        return new_df

    @staticmethod
    def get_active_contract_adjust_price(data, adjust_type, adjust_method, frequency):
        """
        根据参数计算是否复权
        :param data: 数据
        :param adjust_type: 复权类型
        :param adjust_method: 复权因子
        :param frequency: 频率
        :return: 计算后的数据
        """

        if not adjust_type or frequency in ['tick_l1', 'tick_l2', '1min_gtja']:
            return data

        adjust_fields = ['open', 'close', 'high', 'low', 'limit_up', 'limit_down', 'settlement', 'prev_settlement',
                         'prev_close']
        if adjust_type == 'post':
            if adjust_method in ['prev_close_spread', 'open_spread']:
                for field in adjust_fields:
                    data[field] = data[field] + data[adjust_method]
            else:
                for field in adjust_fields:
                    data[field] = data[field] * data[adjust_method]

        return data

    @staticmethod
    def get_active_contract_process_return_fields(data, fields):
        """
        处理返回字段
        :param data: 主力/次主力合约数据
        :param fields: str or str list--选填，返回字段，默认全部
        :return: 筛选后的主力/次主力合约数据
        """

        if not fields:
            return data

        if isinstance(fields, str):
            return data[[fields]]
        else:
            return data[fields]

    def get_active_contract_process_result(self, data, fields):
        """
        处理返回字段
        :param data: 主力/次主力合约数据
        :param fields: str or str list--选填，返回字段，默认全部
        :return: 筛选后的主力/次主力合约数据
        """

        new_df = data.copy()

        # 整合需求文档中所需的字段
        # 价格相关字段通过 "dfs://dayk"."qc_future_dayk" 获取，通过unique_instrument_id 关联查找
        # 前收盘价(qc_future_dayk也无)
        future_day_data, future_session = self.connect_db(history_option_day_db_table_name,
                                                          history_option_day_db_path)

        # 获取筛选后的主力/次主力合约数据的交易时间和合约代码，用于去qc_future_dayk表中查询其他的缺失字段
        unique_instrument_id_list = new_df["unique_instrument_id"].tolist()
        future_filter_df = future_day_data.where(f"unique_instrument_id in {unique_instrument_id_list}").toDF()
        future_session.close()

        future_filter_df_unique = future_filter_df.drop_duplicates(
            subset=['trading_day', 'unique_instrument_id'],
            keep='first'  # 或者 'last'，取决于你要保留哪一个
        )

        merged_df = new_df.merge(
            future_filter_df_unique[['trading_day', 'unique_instrument_id',
                                     'pre_settlement_price', 'open_price',
                                     'highest_price', 'lowest_price', 'close_price',
                                     'settlement_price', 'volume', 'turnover', 'open_interest']],
            on=['trading_day', 'unique_instrument_id'],
            how='left'  # 使用 left join 保留 new_df 的所有行
        )

        # 统一字段（将数据表中的字段重命名成需求文档要求的字段）
        merged_df.rename(columns={'instrument_id': 'order_book_id', 'product_id': 'code',
                                  'exchange_id': 'exchange', 'trading_day': 'date'}, inplace=True)
        merged_df["active_type"] = merged_df["rank"].map({1: "active", 2: "next_active"})

        if fields:
            # 根据fields返回用户需要的字段
            merged_df = merged_df[fields] if isinstance(fields, str) else merged_df[[field for field in fields]]

        return merged_df

    """ get_basic_data 库存/基差/现货价格-数据（日频） """

    def get_basic_data(self, order_book_id, asset_type, start_date, end_date):
        """
        获取库存/基差/现货价格-数据（日频）接口
        :param order_book_id: str--必填，合约代码
        :param asset_type: str--必填，枚举值：库存、基差、现货
        :param start_date: str, datetime.date, datetime.datetime, pandasTimestamp--必填，开始日期
        :param end_date: str, datetime.date, datetime.datetime, pandasTimestamp--必填，结束日期
        :return: 库存/基差/现货价格-数据（日频）
        """

        """ 校验参数 """
        if start_date and end_date:
            if not self.validate_dates(start_date, end_date):
                return None

        self.get_basic_data_validate_params(order_book_id, asset_type, start_date, end_date)

        """ 获取数据 """
        data, db_session = self.get_basic_data_get_data(order_book_id, asset_type, start_date, end_date)
        db_session.close()

        """ 处理结果 """
        data = self.get_basic_data_handle_data(data, asset_type)

        return data

    def get_basic_data_validate_params(self, order_book_id, asset_type, start_date, end_date):
        """
        校验参数
        :param order_book_id: 合约代码
        :param asset_type: 数据类型： 库存、现货、基差
        :param start_date:   开始日期
        :param end_date:    结束日期
        :return:
        """

        # 校验必填参数
        self.get_basic_data_validate_required_params(order_book_id, asset_type, start_date, end_date)

        # 校验order_book_id 类型
        self.get_basic_data_validate_order_book_id(order_book_id)

        # 校验asset_type 类型
        self.get_basic_data_validate_asset_type(asset_type)

        # 校验start_date 和 end_date 类型
        self.get_basic_data_validate_date(start_date, end_date)

    def get_basic_data_validate_required_params(self, order_book_id, asset_type, start_date, end_date):
        params_dict = {
            "order_book_id": order_book_id,
            "asset_type": asset_type,
            "start_date": start_date,
            "end_date": end_date
        }
        for key, value in params_dict.items():
            self.general_validate_params_required(value, key)  # 校验必填参数

    def get_basic_data_validate_order_book_id(self, order_book_id):
        """
        校验order_book_id 类型
        :param order_book_id: str--必填，合约代码
        :return: None
        """

        self.general_validate_param_is_str("order_book_id", order_book_id)

    def get_basic_data_validate_asset_type(self, asset_type):
        """
        校验asset_type 类型
        :param asset_type: str--必填，枚举值：库存、基差、现货
        :return: None
        """

        self.general_validate_param_is_str("asset_type", asset_type)

    def get_basic_data_validate_date(self, start_date, end_date):
        """
        校验start_date 和 end_date 类型
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: None
        """

        self.format_date(start_date)
        self.format_date(end_date)

        # error_msg = "start_date or end_date type error, datetime.date, datetime.datetime, pandasTimestamp type or can be converted to the type"

        # # 校验start_date 和 end_date 是否为datetime.date, datetime.datetime, pandasTimestamp类型或者可以转换成该类型的str
        # if isinstance(start_date, (str, datetime.date, datetime.datetime, pd.Timestamp)) and isinstance(end_date, (
        #         str, datetime.date, datetime.datetime, pd.Timestamp)):
        #     if isinstance(start_date, str) and not self.general_validate_date(start_date):
        #         raise ValueError(error_msg)
        #     if isinstance(end_date, str) and not self.general_validate_date(end_date):
        #         raise ValueError(error_msg)
        # else:
        #     raise ValueError(error_msg)

    def get_basic_data_get_data(self, order_book_id, asset_type, start_date, end_date):
        """
        获取get_basic_data数据
        :param order_book_id: 合约代码
        :param asset_type: 数据类型：库存、基差、现货
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 从对应数据库中获取的数据

        """

        # 根据 asset_type 获取对应的表名和数据库路径
        table_name, db_path = self._get_basic_data_get_table_info(asset_type)
        # 获取数据
        get_basic_data_data, db_session = self.connect_db(table_name, db_path)

        # 根据 order_book_id 筛选数据（应该是从 product_id 品种名称 进行筛选）
        # 使用 DolphinDB 的 where 子句筛选数据
        # 目前库存表中暂无 product_id 字段，后续会添加此字段，以此统一查询数据 2024-12-27
        product_data = get_basic_data_data.where(f"product_id='{order_book_id}'") if isinstance(order_book_id, str) \
            else get_basic_data_data.where(f"product_id in {order_book_id}")

        ''' 
        根据 start_date 和 end_date 筛选数据
        由于库存表和基差表（现货和基差数据在同一张表）数据字段不同，所以此处的筛选需要进行判断
        此处的日期筛选方式不一样是因为 dolphindb 的表设置的字段以及类型不同，
        库存表的 data_date 字段为 STRING 类型，筛选日期时，需要提供和表中格式一致的数据，才能筛选，例如：2024-12-01
        '''
        # 将日期转换为 DolphinDB 的时间格式
        # start_dolphin_date = self._get_basic_data_date_to_dolphin_time(start_date, asset_type)
        # end_dolphin_date = self._get_basic_data_date_to_dolphin_time(end_date, asset_type)
        start_dolphin_date = self.format_date(start_date)
        end_dolphin_date = self.format_date(end_date)

        # 此处还需要判断的原因是，因为对 dolphindb 中不同的日期数据类型查询数据的语法不同
        asset_type_data = product_data.where(
            f"data_date>={start_dolphin_date} and data_date<={end_dolphin_date}") if asset_type == '库存' \
            else product_data.where(f"date>={start_dolphin_date} and date<={end_dolphin_date}")

        return asset_type_data.toDF(), db_session

    def _get_basic_data_date_to_dolphin_time(self, date, asset_type):
        """
        将日期字符串格式化为 'YYYY.MM.DD HH:mm:ss' 格式。
        : params date: 日期字符串，例如 '2018-01-04 09:01:00'
        : params asset_type: 资产类型，例如 '基差' 或 '库存'
        : return ：
            格式化后的日期字符串，例如 '2018.01.04 09:01:00'。
        """

        if isinstance(date, str):
            return datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%Y.%m.%d %H:%M:%S') if (
                self.general_validate_date_str_is_datetime_type(date)) else (
                datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%Y.%m.%d'))
        return date.strftime('%Y.%m.%d %H:%M:%S') if (
            self.general_validate_date_str_is_datetime_type(date)) else date.strftime('%Y.%m.%d')

    @staticmethod
    def _get_basic_data_get_table_info(asset_type):
        """
        获取表信息
        需要程序自行判断合约代码是期货还是期权（根据期货/期权合约信息表中的 mk_instrument_id 和 instrument_id 进行筛选）
        mk_instrument_id: 米筐合约代码， instrument_id: CTP合约代码
        Args:
            asset_type: 资产类型
        Returns:
            表信息
        Raises:
            ValueError: 如果频率不在 ['现货', '基差', '库存']中, 则抛出异常
        """
        try:
            return {
                "现货": (spot_db_table_name, spot_db_path),
                "库存": (inventory_db_table_name, inventory_db_path),
                "基差": (basis_db_table_name, basis_db_path),
            }.get(asset_type)
        except ValueError:
            raise Exception("asset_type must be in ['现货', '基差', '库存']")

    @staticmethod
    def get_basic_data_handle_data(data, asset_type):
        """
        处理返回结果
        :param data: 返回结果
        :param asset_type: 资产类型
        :return: 处理后的返回结果
        """

        new_df = data.copy()

        new_df["asset_type"] = asset_type
        # 处理基差/现货
        if asset_type in ["现货", "基差"]:
            new_df.rename(columns={'product_id': 'order_book_id',
                                   'futures_price' if asset_type == '现货' else 'main_basis': 'value'
                                   }, inplace=True)
        # 处理库存
        else:
            new_df.rename(columns={'product_id': 'order_book_id', 'data_date': 'date', 'inventory_value': 'value'},
                          inplace=True)

        return new_df[['order_book_id', 'asset_type', 'date', 'value']]

    """ get_warehouse_stocks_future 仓单数据 """

    def get_warehouse_stocks_future(self, commodity=None, start_date=None,
                                    end_date=datetime.date.today() - datetime.timedelta(days=1)):
        """
        获取仓单数据
        :param commodity: str--必填，期货合约品种
        :param start_date: str--必填，开始日期
        :param end_date: str--必填，结束日期 (默认为策略当天日期的前一天)
        :return: 仓单数据
        """

        """ 校验必填参数 """
        if start_date and end_date:
            if not self.validate_dates(start_date, end_date):
                return None

        # 校验commodity, start_date, end_date 是否为必填参数
        self.get_warehouse_stocks_future_validate_required_params(commodity, start_date, end_date)

        # 校验commodity, start_date, end_date 是否为str类型
        self.get_warehouse_stocks_future_validate_type_str(commodity)

        # 校验start_date, end_date
        start_date = self.format_date_split_by_(start_date)
        end_date = self.format_date_split_by_(end_date)

        """ 获取数据 """
        # 从数据库中获取数据
        data = self.get_warehouse_stocks_future_get_data(commodity, get_warehouse_stocks_future_db_table_name,
                                                         get_warehouse_stocks_future_db_path)

        """ 筛选数据 """
        # 根据日期筛选数据
        data = self.get_warehouse_stocks_future_filter_data_by_date(start_date, end_date, data)

        return data

    def get_warehouse_stocks_future_validate_required_params(self, commodity, start_date, end_date):
        """
        校验仓单数据必填参数
        :param commodity: str--必填，期货合约品种
        :param start_date: str--必填，开始日期
        :param end_date: str--必填，结束日期 (默认为策略当天日期的前一天)
        :return: None
        """

        params_dict = {
            "commodity": commodity,
            "start_date": start_date,
            "end_date": end_date
        }

        for key, value in params_dict.items():
            self.general_validate_params_required(value, key)

    def get_warehouse_stocks_future_validate_type_str(self, commodity):
        """
        校验参数类型是否为str
        :param commodity: str--必填，期货合约品种
        :return: None
        """

        params_dict = {
            "commodity": commodity,
            # "start_date": start_date,
            # "end_date": end_date
        }

        for key, value in params_dict.items():
            self.general_validate_param_is_str(key, value)

    def get_warehouse_stocks_future_get_data(self, commodity, table_name, db_path):
        """
        获取get_basic_data数据
        :param commodity: 期货合约品种
        :param table_name: 表名
        :param db_path: 数据库路径
        :return: 从对应数据库中获取的数据

        """

        get_warehouse_stocks_future_data, db_session = self.connect_db(table_name, db_path)

        filtered_data = pd.DataFrame()
        # 使用 DolphinDB 的 where 子句筛选数据
        if isinstance(commodity, str):
            # 旧表
            # filtered_data = get_warehouse_stocks_future_data.where(f"product_code='{commodity}'").toDF()
            # 新表
            filtered_data = get_warehouse_stocks_future_data.where(f"product_id='{commodity}'").toDF()
        elif isinstance(commodity, list):
            # 旧表
            # filtered_data = get_warehouse_stocks_future_data.where(f"product_code in {commodity}").toDF()
            # 新表
            filtered_data = get_warehouse_stocks_future_data.where(f"product_id in {commodity}").toDF()

        # 关闭数据库连接
        # db_session.close()  # 用了数据库信息后，需要取消注释

        return filtered_data

    def get_warehouse_stocks_future_filter_data_by_date(self, start_date, end_date, data):
        """
        根据日期过滤get_basic_data数据
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param data: 数据

        :return: 过滤后的数据
        """

        start_date = self._get_warehouse_stocks_future_date_conversion(start_date)
        end_date = self._get_warehouse_stocks_future_date_conversion(end_date)

        # 根据转换后的日期过滤数据
        data = data[
            (data['trading_day'] >= start_date) & (
                    data['trading_day'] <= end_date)]

        return data

    def _get_warehouse_stocks_future_date_conversion(self, date_str):
        """
        将日期字符串转换成对应格式的日期数据
        :param date_str: 日期字符串
        :return: 转换后的日期数据
        """

        if isinstance(date_str, str):
            # return self.general_date_str_to_datetime(date_str)

            if self.general_validate_date_str_is_datetime_type(date_str):
                return self.general_date_str_to_datetime(date_str)
            if self.general_validate_date_str_is_date_type(date_str):
                return self.general_date_str_to_date(date_str)

        return date_str

    """ get_vwap 获取vwap成交量加权价格指标 """

    def get_vwap(self, order_book_ids=None, start_date=None, end_date=None, frequency='1d', is_batch=False,
                 batch_size=1000000):
        """
        获取vwap成交量加权价格指标
        :param order_book_ids: str OR str list--必填, 合约代码
        :param start_date: datetime--必填,  开始日期
        :param end_date: datetime--必填, 结束日期
        :param frequency: str--必填, 历史数据的频率
        :param is_batch: bool--非必填, 是否批量获取数据
        :param batch_size: int--非必填, 批量获取数据时，每次获取数据的条数
        :return: vwap成交量加权价格指标
        """

        """ 校验必填参数 """
        if start_date and end_date:
            if not self.validate_dates(start_date, end_date):
                return None

        # 校验oder_book_ids, start_date, end_date, frequency 是否为必填参数
        self.get_vwap_validate_required_params(order_book_ids, start_date, end_date, frequency)

        # 校验order_book_ids是否为str OR str list
        self.get_vwap_validate_order_book_ids(order_book_ids)

        # 校验start_date, end_date是否为datetime 或 对应格式的字符串
        self.get_vwap_validate_date_type(start_date, end_date)

        # 校验frequency是否为str
        self.get_vwap_validate_frequency(frequency)

        """  获取数据 """
        # 根据frequency获取数据
        total_data, db_session = self.get_vwap_get_data(frequency, order_book_ids, start_date, end_date)

        if is_batch:  # 如果需要分批次处理数据
            for i in range(0, total_data.rows, batch_size):
                # 分批次从dolphindb获取数据，转换成dataframe（因为数据量过大时，将tables对象转换成dataframe比较耗时）
                data = total_data.limit([i, batch_size]).toDF()

                # 重命名字段
                data = self.rename_vwap_columns(data)

                # 使用 yield from 将数据添加到列表中
                yield from [data[["order_book_id", "date", "vwap_value"]]]

            # 关闭数据库连接
            db_session.close()
        else:  # 如果不需要分批次处理数据
            # 分批将dolphindb获取的数据转换成dataframe
            data = self._get_vwap_data_todf(total_data)

            ''' 数据处理 '''
            # 重命名字段
            data = self.rename_vwap_columns(data)

            yield data[["order_book_id", "date", "vwap_value"]]

            # 关闭数据库连接
            db_session.close()

    @staticmethod
    def _get_vwap_data_todf(data):
        """
        用于接收从数据库获取的数据，并分批处理，将其转换成dataframe格式的数据返回
        : params data: 从数据库获取的数据
        : return : 转换成dataframe格式后的数据
        """

        result = pd.DataFrame()
        if data.rows > 1000000:
            chunk_size, start = 1000000, 0
            while start < data.rows:
                limit_data = data.limit([start, chunk_size]).toDF()
                result = limit_data if result.empty else pd.concat([result, limit_data], ignore_index=True)
                start += chunk_size

            return result
        return data.toDF()

    def get_vwap_validate_required_params(self, order_book_ids, start_date, end_date, frequency):
        """
        校验必填参数
        :param order_book_ids: str OR str list--必填, 合约代码
        :param start_date: datetime--必填,  开始日期
        :param end_date: datetime--必填, 结束日期
        :param frequency: str--必填, 历史数据的频率
        :return: None
        """

        params_dict = {
            "order_book_ids": order_book_ids,
            "start_date": start_date,
            "end_date": end_date,
            "frequency": frequency
        }

        for key, value in params_dict.items():
            self.general_validate_params_required(value, key)

    def get_vwap_validate_order_book_ids(self, order_book_ids):
        """
        校验order_book_ids参数类型是否为str OR str list
        :param order_book_ids: str OR str list--必填, 合约代码
        :return: None
        """

        self.general_validate_field_str_or_list(order_book_ids, "order_book_ids")

    def get_vwap_validate_date_type(self, start_date, end_date):
        """
        校验start_date和end_date参数类型是否为datetime
        :param start_date: datetime--必填,  开始日期
        :param end_date: datetime--必填, 结束日期
        :return: None
        """

        # self._get_vwap_validate_date_type(start_date, "start_date")
        # self._get_vwap_validate_date_type(end_date, "end_date")
        self.format_date(start_date)
        self.format_date(end_date)

    def _get_vwap_validate_date_type(self, date_str, date_str_name):
        """
        校验date_str参数类型是否为datetime格式的字符串
        :param date_str: str, 日期
        :return: None
        """

        if isinstance(date_str, str) and not self.general_validate_date_str_is_datetime_type(date_str):
            raise ValueError(f"{date_str_name} type error, datetime.datetime type or can be converted to the type")
        if not isinstance(date_str, str) and not isinstance(date_str, datetime.datetime):
            raise ValueError(f"{date_str_name} type error, datetime.datetime type or can be converted to the type")

    def _get_vwap_date_conversion(self, date_str):
        """
        将日期字符串转换成对应格式的日期数据
        :param date_str: 日期字符串
        :return: 转换后的日期数据
        """

        if isinstance(date_str, str):
            if self.general_validate_date_str_is_datetime_type(date_str):
                return self.general_date_str_to_datetime(date_str)
            if self.general_validate_date_str_is_date_type(date_str):
                return self.general_date_str_to_date(date_str).date()

        return date_str

    def get_vwap_get_data(self, frequency, order_book_ids, start_date, end_date):
        """
        获取vwap数据
        :param frequency: 频率
        :param order_book_ids: 合约代码
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: vwap数据
        """

        vwap_dict = {
            "1m": {
                "table_name": vwap_min_db_table_name,
                "db_path": vwap_min_db_path
            },
            "1d": {
                "table_name": vwap_day_db_table_name,
                "db_path": vwap_day_db_path
            }
        }

        table_result = vwap_dict.get(frequency, (None, None))
        table_name = table_result["table_name"]
        db_path = table_result["db_path"]

        data, db_session = self._get_vwap_get_data(order_book_ids, table_name, db_path, start_date, end_date)

        return data, db_session

    @staticmethod
    def get_vwap_format_date(date_str):
        """将日期字符串格式化为 'YYYY.MM.DD HH:mm:ss' 格式。
        : params date_str: 日期字符串，例如 '2018-01-04 09:01:00'。
        : return ：
            格式化后的日期字符串，例如 '2018.01.04 09:01:00'。
        """
        if isinstance(date_str, str):
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            return date_obj.strftime('%Y.%m.%d %H:%M:%S')
        return date_str.strftime('%Y.%m.%d %H:%M:%S')

    def _get_vwap_get_data(self, order_book_ids, table_name, db_path, start_date, end_date):
        """
        用于接收数据表以及数据库，获取数据
        : params order_book_ids: 合约代码
        : params table_name: 数据表路径
        : params db_path: 数据库路径
        : params start_date: 开始时间
        : params end_date: 结束时间

        : return limit_data: 从数据库获取并根据合约代码筛选后的数据
        """

        get_vwap_data, db_session = self.connect_db(table_name, db_path)

        # 使用 DolphinDB 的 where 子句筛选数据
        if isinstance(order_book_ids, str):
            limit_data = get_vwap_data.where(f"instrument_id='{order_book_ids}'")
        else:
            limit_data = get_vwap_data.where(f"instrument_id in {order_book_ids}")

        # 将日期转换成 DolphinDB 识别的日期格式，用于筛选数据
        # format_start_date = self.get_vwap_format_date(start_date)
        # format_end_date = self.get_vwap_format_date(end_date)
        format_start_date = self.format_date(start_date)
        format_end_date = self.format_date(end_date)

        # 根据日期对数据再次进行筛选，最大程度减轻数据库压力
        limit_data = limit_data.where(f"trade_time >= {format_start_date} and trade_time <= {format_end_date}").where(
            "metric='vwap'")

        return limit_data, db_session

    # 重命名字段名称
    @staticmethod
    def rename_vwap_columns(data):
        """
        此方法用于重命名字段名称
        :param data: 数据
        :return: 重命名后的数据

        """

        vwap_fields_dict = {
            "instrument_id": "order_book_id", "trade_time": "date", "value": "vwap_value"
        }

        rename_data = data.rename(columns=vwap_fields_dict)

        return rename_data

    def get_vwap_validate_frequency(self, frequency):
        """
        校验frequency参数类型是否为str格式的字符串
        :param frequency: str, 历史数据的频率
        :return: None
        """

        self.general_validate_param_is_str("frequency", frequency)

    """ get_twap 获取twap时间加权价格 """

    def get_twap(self, order_book_ids=None, start_date=None, end_date=None, frequency='1d', is_batch=False,
                 batch_size=1000000):
        """
        获取twap成交量加权价格指标
        :param order_book_ids: str OR str list--必填, 合约代码
        :param start_date: datetime--必填,  开始日期
        :param end_date: datetime--必填, 结束日期
        :param frequency: str--必填, 历史数据的频率
        :param is_batch: bool--选填, 是否批量获取数据
        :param batch_size: int--选填, 批量获取数据时每次获取的条数
        :return: twap成交量加权价格指标
        """

        """ 校验必填参数 """
        if start_date and end_date:
            if not self.validate_dates(start_date, end_date):
                return None
        # 校验oder_book_ids, start_date, end_date, frequency 是否为必填参数
        self.get_twap_validate_required_params(order_book_ids, start_date, end_date, frequency)

        # 校验order_book_ids是否为str OR str list
        self.get_twap_validate_order_book_ids(order_book_ids)

        # 校验start_date, end_date是否为datetime 或 对应格式的字符串
        self.get_twap_validate_date_type(start_date, end_date)

        # 校验frequency是否为str
        self.get_twap_validate_frequency(frequency)

        """  获取数据 """
        # 根据frequency获取数据
        total_data, db_session = self.get_twap_get_data(frequency, order_book_ids, start_date, end_date)

        if is_batch:  # 如果需要分批次处理数据
            for i in range(0, total_data.rows, batch_size):
                # 分批次从dolphindb获取数据，转换成dataframe（因为数据量过大时，将tables对象转换成dataframe比较耗时）
                data = total_data.limit([i, batch_size]).toDF()

                # 重命名字段
                data = self.rename_twap_columns(data)

                # 使用 yield from 将数据添加到列表中
                yield from [data[["order_book_id", "date", "vwap_value"]]]

            # 关闭数据库连接
            db_session.close()
        else:  # 如果不需要分批次处理数据
            # 分批将dolphindb获取的数据转换成dataframe
            data = self._get_vwap_data_todf(total_data)

            ''' 数据处理 '''
            # 重命名字段
            data = self.rename_twap_columns(data)

            yield data[["order_book_id", "date", "vwap_value"]]

            # 关闭数据库连接
            db_session.close()

    # 重命名字段名称
    @staticmethod
    def rename_twap_columns(data):
        """
        此方法用于重命名字段名称
        :param data: 数据
        :return: 重命名后的数据

        """

        twap_fields_dict = {
            "instrument_id": "order_book_id", "trade_time": "date", "value": "vwap_value"
        }

        rename_data = data.rename(columns=twap_fields_dict)

        return rename_data

    def get_twap_validate_required_params(self, order_book_ids, start_date, end_date, frequency):
        """
        校验必填参数
        :param order_book_ids: str OR str list--必填, 合约代码
        :param start_date: datetime--必填,  开始日期
        :param end_date: datetime--必填, 结束日期
        :param frequency: str--必填, 历史数据的频率
        :return: None
        """

        params_dict = {
            "order_book_ids": order_book_ids,
            "start_date": start_date,
            "end_date": end_date,
            "frequency": frequency
        }

        for key, value in params_dict.items():
            self.general_validate_params_required(value, key)

    def get_twap_validate_order_book_ids(self, order_book_ids):
        """
        校验order_book_ids参数类型是否为str OR str list
        :param order_book_ids: str OR str list--必填, 合约代码
        :return: None
        """

        self.general_validate_field_str_or_list(order_book_ids, "order_book_ids")

    def get_twap_validate_date_type(self, start_date, end_date):
        """
        校验start_date和end_date参数类型是否为datetime
        :param start_date: datetime--必填,  开始日期
        :param end_date: datetime--必填, 结束日期
        :return: None
        """

        self.format_date(start_date)
        self.format_date(end_date)

        # self._get_twap_validate_date_type(start_date, "start_date")
        # self._get_twap_validate_date_type(end_date, "end_date")

    def _get_twap_validate_date_type(self, date_str, date_str_name):
        """
        校验date_str参数类型是否为datetime格式的字符串
        :param date_str: str, 日期
        :return: None
        """

        if isinstance(date_str, str) and not self.general_validate_date_str_is_datetime_type(date_str):
            raise ValueError(f"{date_str_name} type error, datetime.datetime type or can be converted to the type")
        if not isinstance(date_str, str) and not isinstance(date_str, datetime.datetime):
            raise ValueError(f"{date_str_name} type error, datetime.datetime type or can be converted to the type")

    def get_twap_get_data(self, frequency, order_book_ids, start_date, end_date):
        """
        获取twap数据
        :param frequency: 频率
        :param order_book_ids: 合约代码
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: twap数据
        """

        twap_dict = {
            "1m": {
                "table_name": twap_min_db_table_name,
                "db_path": twap_min_db_path
            },
            "1d": {
                "table_name": twap_day_db_table_name,
                "db_path": twap_day_db_path
            }
        }

        table_result = twap_dict.get(frequency, (None, None))
        table_name = table_result["table_name"]
        db_path = table_result["db_path"]

        data, db_session = self._get_twap_get_data(order_book_ids, table_name, db_path, start_date, end_date)

        return data, db_session

    def _get_twap_get_data(self, order_book_ids, table_name, db_path, start_date, end_date):
        """
        用于接收数据表以及数据库，获取数据
        : params order_book_ids: 合约代码
        : params table_name: 数据表路径
        : params db_path: 数据库路径
        : params start_date: 开始时间
        : params end_date: 结束时间

        : return limit_data: 从数据库获取并根据合约代码筛选后的数据
        """

        get_vwap_data, db_session = self.connect_db(table_name, db_path)

        # 使用 DolphinDB 的 where 子句筛选数据
        if isinstance(order_book_ids, str):
            limit_data = get_vwap_data.where(f"instrument_id='{order_book_ids}'")
        else:
            limit_data = get_vwap_data.where(f"instrument_id in {order_book_ids}")

        # 将日期转换成 DolphinDB 识别的日期格式，用于筛选数据
        # format_start_date = self.get_twap_format_date(start_date)
        # format_end_date = self.get_twap_format_date(end_date)

        format_start_date = self.format_date(start_date)
        format_end_date = self.format_date(end_date)

        # 根据日期对数据再次进行筛选，最大程度减轻数据库压力
        limit_data = limit_data.where(f"trade_time >= {format_start_date} and trade_time <= {format_end_date}").where(
            "metric='twap'")

        return limit_data, db_session

    @staticmethod
    def get_twap_format_date(date_str):
        """将日期字符串格式化为 'YYYY.MM.DD HH:mm:ss' 格式。
        : params date_str: 日期字符串，例如 '2018-01-04 09:01:00'。
        : return ：
            格式化后的日期字符串，例如 '2018.01.04 09:01:00'。
        """
        if isinstance(date_str, str):
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            return date_obj.strftime('%Y.%m.%d %H:%M:%S')
        return date_str.strftime('%Y.%m.%d %H:%M:%S')

    def get_twap_validate_frequency(self, frequency):
        """
        校验frequency参数类型是否为str格式的字符串
        :param frequency: str, 历史数据的频率
        :return: None
        """

        self.general_validate_param_is_str("frequency", frequency)

    """ 实时分钟k线订阅接口封装 """

    def subscribe(self, subscribe_ip=None, subscribe_port=None, subscribe_user_id=None, subscribe_password=None,
                  is_batch=True, batch_size=10, order_book_ids=None, frequency=None, fields=None, offset=-1):
        """
        实时分钟k线订阅接口封装
        :param subscribe_ip: 订阅ip
        :param subscribe_port: 订阅端口
        :param subscribe_user_id: 订阅用户id
        :param subscribe_password: 订阅用户密码
        :param is_batch: 是否批量订阅
        :param batch_size: 订阅数据批次大小
        :param order_book_ids: 订阅合约代码 str or str list(必填)
        :param frequency: 订阅频率 str (必填)
        :param fields: 订阅字段 str or str list
        :param offset: 从当前开始订阅还是从头订阅 -1:当前，0:从头开始
        """

        """ 校验必填参数 """
        # 校验参数是否必填
        self.general_validate_params_required(order_book_ids, "order_book_ids")  # 校验order_book_ids
        self.general_validate_params_required(frequency, "frequency")  # 校验frequency

        # 校验参数类型
        self.general_validate_field_str_or_list(order_book_ids, "order_book_ids")  # 校验order_book_ids是否为str或str list
        self.general_validate_param_is_str("frequency", frequency)  # 校验frequency是否为str

        s = ddb.session()
        s.connect(subscribe_ip, subscribe_port, subscribe_user_id, subscribe_password)

        s.enableStreaming()

        subscribe_fields = ["trading_day", "instrument_id", "trade_time", "open_price", "highest_price", "lowest_price",
                            "close_price",
                            "volume", "turnover", "open_interest"]

        def handler(lst):
            """
            回调函数，用于对返回的结果进行各种处理
            """

            if is_batch:
                # 根据order_book_ids过滤数据
                if isinstance(order_book_ids, str):
                    filter_df = lst[lst['instrument_id'] == order_book_ids]
                else:
                    filter_df = lst[lst['instrument_id'].isin(order_book_ids)]

                filter_df = filter_df[subscribe_fields]  # 根据subscribe_fields进行字段筛选
                # 根据fields进行字段筛选
                if fields:
                    filter_df = filter_df[fields] if isinstance(fields, list) else filter_df[[fields]]

                if not filter_df.empty:
                    # 输出筛选后的数据
                    print("\n", filter_df)  # 处理接收到的数据
            else:
                print(lst)

        async def subscribe_data(is_subscribe, batch_num):
            if is_subscribe:
                s.subscribe(subscribe_ip, subscribe_port, handler, subscribe_min_db_table_name, actionName="new_action",
                            offset=offset, batchSize=batch_num, throttle=0.1, msgAsTable=True)
            else:
                s.subscribe(subscribe_ip, subscribe_port, handler, subscribe_min_db_table_name, actionName="new_action",
                            offset=offset)
            while True:
                await asyncio.sleep(1)

        async def subscribe_minute_kline(is_subscribe, batch_num):
            """
            实时订阅分钟k线接口封装
            """

            await (subscribe_data(is_subscribe, batch_num))

        try:
            asyncio.run(subscribe_minute_kline(is_batch, batch_size))
        except KeyboardInterrupt:
            print("Subscription stopped by user.")
            # 关闭连接和资源释放逻辑
            s.unsubscribe(subscribe_ip, subscribe_port, subscribe_min_db_table_name)
        except Exception as e:
            raise e

    """ 
    get_history_bars 此接口和下面的接口合并为一个，根据传入的参数进行判断，调用不同的方法
    查询合约指定日期前的行情数据（2024-12-24提出） 
    """

    def get_history_bars(self, datetime_str=None, instrument_id=None, bar_count=None,
                         frequency=None, fields=None, start_date=None, end_date=None):
        """
        （此接口根据接收的参数调用不同的功能函数）
        查询合约指定日期时间前的行情数据
        需要程序自行判断合约代码是期货还是期权（根据期货/期权合约信息表中的 mk_instrument_id 和 instrument_id 进行筛选）
        mk_instrument_id: 米筐合约代码， instrument_id: CTP合约代码
        Args:
            datetime_str: str, 查询的日期时间，格式为'YYYY.MM.DD'
            instrument_id: str or List[str], 合约代码，可以是单个合约或合约列表
            bar_count: int, 获取的历史K线数量
            frequency: str, 历史行情频率，可选值：'1d'或'1m'
            fields: str, 返回的数据字段，如'close_price'表示收盘价
            start_date: str, 开始日期，格式为'YYYY.MM.DD' （此接口根据接收的参数调用不同的功能函数）
            end_date: str, 结束日期，格式为'YYYY.MM.DD' （此接口根据接收的参数调用不同的功能函数）
        Returns:
            如果instrument_id是字符串，返回一个浮点数列表 [619.70, 620.20, 618.40, 622.00, 610.10]
            如果instrument_id是列表，返回一个浮点数列表的列表 [[619.70, 620.20], [618.40, 622.00]]
        Raises:
            ValueError: 参数验证失败时抛出
        """

        ''' 根据参数的不同，调用不同的函数 '''
        if datetime_str and bar_count is not None:
            # 参数验证
            self._get_history_bar_validate_params(datetime_str, instrument_id, bar_count, frequency, fields)

            # 转换日期格式
            query_time = self._get_history_bar_parse_datetime(datetime_str)

            # 执行查询并筛选数据
            result, bar_db_session = self._get_history_bar_execute_query(frequency, instrument_id, query_time,
                                                                         bar_count)
            # 此处在所有的查询筛选都在数据库层面进行完后，再关闭连接
            # 如果将dolphindb的Table对象转换成DataFrame时，如果数据量较大，那么需要耗费的时间较长，所以尽可能将所有的筛选在数据库层面完成
            bar_db_session.close()

            # 处理结果
            return self._get_history_bar_process_result(result, instrument_id, fields, bar_count)
        else:
            return self.get_history_bar(instrument_id, start_date, end_date, frequency, fields)

    def _get_history_bar_validate_params(self, datetime_str, instrument_id, bar_count,
                                         frequency, fields):
        """
        验证输入参数的有效性
        Args:
            datetime_str (str): 日期字符串
            instrument_id (str or list): 合约ID
            bar_count (int): 查询的K线数量
            frequency (str): K线频率
            fields (str): 查询的字段
        Raises:
            ValueError: 参数验证失败时抛出
        """
        # 验证时间格式
        if not datetime_str or not isinstance(datetime_str, str):
            raise ValueError("datetime_str must be a non-empty string")
        # if not self._get_history_bar_is_convertible_datetime(datetime_str):
        #     raise ValueError("datetime_str must be in the format 'YYYY-MM-DD HH:MM:SS'")

        # 验证合约代码
        self.general_validate_field_str_or_list(instrument_id, "instrument_id")
        self.general_validate_params_required(instrument_id, "instrument_id")

        # 验证K线数量
        # if not isinstance(bar_count, int) or bar_count <= 0:
        #     raise ValueError("bar_count must be a positive integer")

        # 验证频率
        if frequency not in ['1d', '1m']:
            raise ValueError("frequency must be '1d' or '1m'")

        # 验证字段
        if not isinstance(fields, str) or not fields:
            raise ValueError("fields must be a non-empty string")

    @staticmethod
    def _get_history_bar_is_convertible_datetime(date_data):
        """
        判断 date_data 是否是 datetime 类型或可以转换成 datetime 类型的字符串，并精确到秒。
        param: date_data: 要判断的值。

        Returns:
            True 如果 start_date 是 datetime 类型或可以转换成 datetime 类型的字符串，否则 False。
        """

        if isinstance(date_data, datetime.datetime):
            return True
        elif isinstance(date_data, str):
            try:
                datetime.datetime.strptime(date_data, "%Y-%m-%d %H:%M:%S")
                return True
            except ValueError:
                return False
        else:
            return False

    # @staticmethod
    def _get_history_bar_parse_datetime(self, datetime_str):
        """
        解析日期时间字符串
        Args:
            datetime_str: 日期时间字符串，格式为'YYYY-MM-DD HH:MM:SS'
        Returns:
            datetime.datetime 格式的datetime_str
        Raises:
            ValueError: 如果datetime_str不是有效的日期时间字符串

        """

        return self.format_date(datetime_str)

        # try:
        #     return datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S') if isinstance(datetime_str, str) \
        #         else datetime_str
        # except ValueError:
        #     raise ValueError("Invalid datetime format, should be 'YYYY-MM-DD HH:MM:SS'")

    def _get_history_bar_execute_query(self, frequency, instrument_id, datetime_str, bar_count):
        """
        执行查询
        Args:
            frequency: 频率，'1d' 或 '1m'
            instrument_id: 合约代码
            datetime_str: 日期时间字符串，格式为'YYYY-MM-DD HH:MM:SS'
            bar_count: 查询的条数
        Returns:
            查询结果
        """

        # 获取表信息
        table_info = self._get_history_bar_get_table_info(frequency, instrument_id)

        # 获取数据
        table_data, bar_db_session = self.connect_db(table_info[0], table_info[1])

        # 筛选数据
        query_data = self._get_history_bar_filter_data(table_data, instrument_id, datetime_str, bar_count)

        return query_data.toDF(), bar_db_session

    def _get_history_bar_get_table_info(self, frequency, instrument_id):
        """
        获取表信息
        需要程序自行判断合约代码是期货还是期权（根据期货/期权合约信息表中的 mk_instrument_id 和 instrument_id 进行筛选）
        mk_instrument_id: 米筐合约代码， instrument_id: CTP合约代码
        Args:
            frequency: 频率
            instrument_id: 合约代码
        Returns:
            表信息
        Raises:
            ValueError: 如果频率不在['1d', '1min']中, 则抛出异常
        """
        contract_type = self.filter_contract_type(instrument_id)

        if contract_type == "future":
            return {
                "1d": (history_future_day_db_table_name, history_future_day_db_path),
                "1m": (history_future_min_db_table_name, history_future_min_db_path),
            }.get(frequency)
        elif contract_type == "option":
            return {
                "1d": (history_option_day_db_table_name, history_option_day_db_path),
                "1m": (history_option_min_db_table_name, history_option_min_db_path),
            }.get(frequency)
        else:
            raise Exception("frequency is not valid or frequency is not valid for this frequency")

    @staticmethod
    def _get_history_bar_filter_data(table_data, instrument_id, datetime_str, bar_count):
        """
        筛选数据
        Args:
            table_data: 表数据
            instrument_id: 交易代码
            datetime_str: 日期字符串
            bar_count: 条数
        Returns:
            筛选后的数据
        Raises:
            无
        """

        # 将日期转换成 DolphinDB 识别的日期格式，用于筛选数据
        # dolphin_date = self._get_history_bar_datetime_to_dolphin_time(datetime_str)
        dolphin_date = datetime_str

        if isinstance(instrument_id, str):
            query_data = (table_data.where(f"instrument_id='{instrument_id}'")
                          .where(f"trading_day <= {dolphin_date}")
                          .sort("trading_day", ascending=False)
                          .limit(bar_count))

        else:
            query_data = (table_data.where(f"instrument_id in {instrument_id}")
                          .where(f"trading_day <= {dolphin_date}")
                          .sort("trading_day", ascending=False)
                          .limit(bar_count))

        # 根据日期对数据再次进行筛选，最大程度减轻数据库压力
        query_data = query_data.where(f"trade_time <= {dolphin_date}")

        return query_data

    @staticmethod
    def _get_history_bar_datetime_to_dolphin_time(datetime_str):
        """将日期字符串格式化为 'YYYY.MM.DD HH:mm:ss' 格式。
        : params datetime_str: 日期字符串，例如 '2018-01-04 09:01:00'。
        : return ：
            格式化后的日期字符串，例如 '2018.01.04 09:01:00'。
        """
        if isinstance(datetime_str, str):
            date_obj = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            return date_obj.strftime('%Y.%m.%d %H:%M:%S')
        return datetime_str.strftime('%Y.%m.%d %H:%M:%S')

    @staticmethod
    def _get_history_bar_process_result(result, instrument_id, fields, bar_count):
        """
        返回结果处理
        Args:
            result: 未根据instrument_id处理过的数据
            instrument_id: 合约代码
            fields: 返回的字段
            bar_count: 返回的条数
        Returns:
            result: 返回结果
        """

        # if isinstance(instrument_id, str):
        #     # 单个合约返回一维列表
        #     return result[fields].tolist()
        # else:
        #     # 多个合约返回二维列表
        #     return [result[result['instrument_id'] == code_id][fields].tolist()
        #             for code_id in instrument_id]

        if isinstance(instrument_id, str):
            # 单个合约返回一维列表
            data = result[fields].tolist()
            # 如果数据长度不足bar_count，用0填充
            if len(data) < bar_count:
                data.extend([0] * (bar_count - len(data)))
            return data
        else:
            # 多个合约返回二维列表
            data = [result[result['instrument_id'] == code_id][fields].tolist() for code_id in instrument_id]
            # 对每个子列表检查长度，不足bar_count时用0填充
            for i in range(len(data)):
                if len(data[i]) < bar_count:
                    data[i].extend([0] * (bar_count - len(data[i])))
            return data

    """ get_history_bars 查询行情指定范围日期的行情数据"""

    def get_history_bar(self, instrument_id, start_date, end_date, frequency, fields=None):
        """
        Args:
            instrument_id: str or List[str], 合约代码，可以是单个合约或合约列表
            start_date: str, 起始日期，格式为'YYYY.MM.DD' ‘2024.01.01'
            end_date: str, 结束日期，格式为'YYYY.MM.DD' '2024.01.05'
            frequency: str, 历史行情频率
            fields: str, 返回的数据字段， 如'close_price'表示收盘价
        Returns:
            result: 查询结果
        """

        # 校验参数
        if start_date and end_date:
            if not self.validate_dates(start_date, end_date):
                return None

        self.get_history_bars_validate_params(instrument_id, start_date, end_date, frequency, fields)

        # 查询数据
        data, bars_db_session = self._get_history_bars_execute_query(frequency, instrument_id, start_date, end_date)
        bars_db_session.close()

        # 处理结果
        return self._get_history_bars_process_result(data, fields, instrument_id)

    def get_history_bars_validate_params(self, instrument_id, start_date, end_date, frequency, fields):

        """
        验证输入参数的有效性
        Args:
            start_date (str): 起始日期，格式为'YYYY.MM.DD'
            end_date (str): 结束日期，格式为'YYYY.MM.DD'
            instrument_id (str or list): 合约ID
            frequency (str): K线频率
            fields (str): 查询的字段
        Raises:
            ValueError: 参数验证失败时抛出
        """
        # 校验时间格式
        # self._get_history_bars_validate_time(start_date)
        # self._get_history_bars_validate_time(end_date)

        # 验证合约代码
        self.general_validate_field_str_or_list(instrument_id, "instrument_id")
        self.general_validate_params_required(instrument_id, "instrument_id")

        # 验证频率
        if frequency not in ['1d', '1m']:
            raise ValueError("frequency must be '1d' or '1m'")

        # # 验证字段
        # if not isinstance(fields, str) or not fields:
        #     raise ValueError("fields must be a non-empty string")

    def _get_history_bars_validate_time(self, datetime_str):
        """
        验证时间参数的有效性
        Args:
            datetime_str: 时间字符串
        Raises:
            ValueError: 参数验证失败时抛出

        """

        # 验证时间格式
        if not datetime_str or not isinstance(datetime_str, str):
            raise ValueError("datetime_str must be a non-empty string")
        if not self._get_history_bars_is_convertible_datetime(datetime_str):
            raise ValueError("datetime_str must be in the format 'YYYY-MM-DD HH:MM:SS'")

    @staticmethod
    def _get_history_bars_is_convertible_datetime(date_data):
        """
        判断 date_data 是否是 datetime 类型或可以转换成 datetime 类型的字符串，并精确到秒。
        param: date_data: 要判断的值。

        Returns:
            True 如果 start_date 是 datetime 类型或可以转换成 datetime 类型的字符串，否则 False。
        """

        if isinstance(date_data, datetime.datetime):
            return True
        elif isinstance(date_data, str):
            try:
                datetime.datetime.strptime(date_data, "%Y-%m-%d %H:%M:%S")
                return True
            except ValueError:
                return False
        else:
            return False

    def _get_history_bars_execute_query(self, frequency, instrument_id, start_date, end_date):
        """
        执行查询
        Args:
            frequency: 频率，'1d' 或 '1m'
            instrument_id: 合约代码
            start_date: 日期时间字符串，格式为'YYYY.MM.DD'
            end_date: 日期时间字符串，格式为'YYYY.MM.DD'
        Returns:
            查询结果
        """

        # 获取表信息
        table_info = self._get_history_bars_get_table_info(frequency, instrument_id)

        # 获取数据
        table_data, bars_db_session = self.connect_db(table_info[0], table_info[1])

        # 转换日期格式
        conv_start_date = self.format_date(start_date)
        conv_end_date = self.format_date(end_date)

        # 筛选数据
        query_data = self._get_history_bars_filter_data(table_data, instrument_id, conv_start_date, conv_end_date)

        return query_data.toDF(), bars_db_session

    def _get_history_bars_get_table_info(self, frequency, instrument_id):
        """
        获取表信息
        需要程序自行判断合约代码是期货还是期权（根据期货/期权合约信息表中的 mk_instrument_id 和 instrument_id 进行筛选）
        mk_instrument_id: 米筐合约代码， instrument_id: CTP合约代码
        Args:
            frequency: 频率
            instrument_id: 合约代码
        Returns:
            表信息
        Raises:
            ValueError: 如果频率不在['1d', '1min']中, 则抛出异常
        """
        contract_type = self.filter_contract_type(instrument_id)

        if contract_type == "future":
            return {
                "1d": (history_future_day_db_table_name, history_future_day_db_path),
                "1m": (history_future_min_db_table_name, history_future_min_db_path),
            }.get(frequency)
        elif contract_type == "option":
            return {
                "1d": (history_option_day_db_table_name, history_option_day_db_path),
                "1m": (history_option_min_db_table_name, history_option_min_db_path),
            }.get(frequency)
        else:
            raise Exception("frequency is not valid or frequency is not valid for this frequency")

    @staticmethod
    def _get_history_bars_filter_data(table_data, instrument_id, start_date, end_date):
        """
        筛选数据
        :param table_data: 表数据
        :param instrument_id: 合约代码
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 筛选后的数据
        """

        # 使用 DolphinDB 的 where 子句筛选数据
        if isinstance(instrument_id, str):
            query_data = (table_data.where(f"instrument_id='{instrument_id}'").where(f"trade_time >= {start_date} and "
                                                                                     f"trade_time <= {end_date}"))
        else:
            query_data = (table_data.where(f"instrument_id in {instrument_id}").where(f"trade_time >= {start_date} and "
                                                                                      f"trade_time <= {end_date}"))

        return query_data

    @staticmethod
    def _get_history_bars_process_result(result, fields, instrument_id):

        """
        返回结果处理
        - 传入一个instrument_id，多个fields，函数会返回一个pandas DataFrame
        - 传入一个instrument_id，一个field，函数会返回pandas Series
        - 传入多个instrument_id，一个field，函数会返回一个pandas DataFrame
        - 传入多个instrument_id，函数会返回一个pandas Panel

        Args:
            result: 未根据instrument_id处理过的数据
            fields: 返回的字段
            instrument_id: 合约代码
        Returns:
            result: 返回结果
        """
        # 将NaN用0填充
        result = result.fillna(0)

        # 处理单个 instrument_id
        if isinstance(instrument_id, str):
            filtered_data = result[result['instrument_id'] == instrument_id]
            if fields:
                if isinstance(fields, list) and len(fields) > 1:
                    # 多个 fields，返回 DataFrame
                    return filtered_data[fields]
                else:
                    # 单个 field，返回 Series
                    return filtered_data[fields] if isinstance(fields, str) else filtered_data[fields[0]]
            else:
                # 没有指定 fields，返回所有列
                return filtered_data

        # 处理多个 instrument_id
        elif isinstance(instrument_id, list):
            if fields:
                if isinstance(fields, list):
                    # 多个 fields，返回 DataFrame
                    data = pd.concat(
                        [result[result['instrument_id'] == code_id][fields] for code_id in instrument_id],
                        # keys=instrument_id, names=['instrument_id']
                    )
                    return data
                else:
                    # 单个 field，返回 DataFrame
                    data = pd.concat(
                        [result[result['instrument_id'] == code_id][[fields]] for code_id in instrument_id],
                        # keys=instrument_id, names=['instrument_id']
                    )
                    return data
            else:
                # 没有指定 fields，返回 MultiIndex DataFrame（替代 Panel，因为在pandas0.2.x开始，Panel就已经弃用了）
                data = pd.concat(
                    [result[result['instrument_id'] == code_id] for code_id in instrument_id],
                    keys=instrument_id, names=['instrument_id']
                )
                return data

        else:
            raise ValueError("instrument_id 必须是字符串或列表")

    """ 查询合约基础信息 """

    def get_instrument(self, instrument_id):
        """
        查询合约基础信息
        :param instrument_id: 合约代码
        :return: 查询结果
        """

        ''' 校验参数 '''
        self.get_instrument_validate_params(instrument_id)

        ''' 查询数据 '''
        data, db_session = self.get_instrument_get_data(instrument_id)  # 获取期货/期权数据
        db_session.close()

        ''' 处理数据 '''
        return self.get_instrument_handle_data(data, instrument_id)

    def get_instrument_validate_params(self, instrument_id):
        """
        校验参数
        :param instrument_id: 合约代码
        :return:
        """

        # 验证合约代码
        self.general_validate_field_str_or_list(instrument_id, "instrument_id")
        self.general_validate_params_required(instrument_id, "instrument_id")

    def get_instrument_get_data(self, instrument_id):
        """
        查询数据
        :param instrument_id: 合约代码
        :return: 查询到的数据
        """

        # 获取表信息(期货/期权合约信息)
        table_info = self._get_instrument_get_table_info(instrument_id)

        # 获取数据
        table_data, bar_db_session = self.connect_db(table_info[0], table_info[1])

        # 筛选数据
        query_data = self._get_instrument_filter_data(table_data, instrument_id)

        return query_data.toDF(), bar_db_session

    def _get_instrument_get_table_info(self, instrument_id):
        """
        获取表信息
        需要程序自行判断合约代码是期货还是期权（根据期货/期权合约信息表中的 mk_instrument_id 和 instrument_id 进行筛选）
        mk_instrument_id: 米筐合约代码， instrument_id: CTP合约代码
        Args:
            instrument_id: 合约代码
        Returns:
            表信息
        Raises:
            ValueError: 如果频率不在['1d', '1min']中, 则抛出异常
        """
        contract_type = self.filter_contract_type(instrument_id)

        if contract_type == "future":
            return future_contract_db_table_name, future_contract_db_path
        elif contract_type == "option":
            return option_contract_db_table_name, option_contract_db_path
        else:
            raise Exception("frequency is not valid or frequency is not valid for this frequency")

    @staticmethod
    def _get_instrument_filter_data(table_data, instrument_id):
        """
        筛选数据
        Args:
            table_data: 表数据
            instrument_id: 交易代码
        Returns:
            筛选后的数据
        Raises:
            无
        """

        # 使用 DolphinDB 的 where 子句筛选数据(这里因为实际需求的原因需要对每个instrument_id进行筛选，所以需要使用 contextby)
        # 根据bar_count 分别对不同的instrument_id 进行筛选
        # 此处的逻辑是，筛选出每个instrument_id距离给定日期最近的前bar_count条数据
        if isinstance(instrument_id, str):
            query_data = table_data.where(f"instrument_id='{instrument_id}'")
        else:
            query_data = table_data.where(f"instrument_id in {instrument_id}")

        return query_data

    def get_instrument_handle_data(self, data, instrument_id):
        """
        处理数据
        :param data: 期货/期权数据
        :param instrument_id: 合约代码
        :return: 处理后的最终数据
        """

        # 获取交易参数表的数据（有一部分字段需要从交易参数表中取）
        trading_params_data, trading_db_session = self.connect_db(trading_params_db_table_name, trading_params_db_path)

        instrument_list = data["instrument_id"].to_list()

        # 筛选所需的字段(交易参数表)
        filter_data = trading_params_data.select(["product_type", "price_tick"]).where(
            f"instrument_id in {instrument_list}").toDF()

        # 关闭数据库连接
        trading_db_session.close()

        result_fields = ["instrument_id", "exchange_id", "instrument_name", "product_id", "product_type",
                         "create_date", "open_date", "expire_date", "basis_price", "volume_multiple",
                         "underlying_instrument_id", "underlying_multiple", "option_type", "strike_price",
                         "price_tick", "limit_price_min_vol"]

        result = pd.DataFrame()

        # 遍历所有字段
        for field in result_fields:
            if field in filter_data.columns:
                # 如果字段在 trading_data 中，提取该列
                result[field] = filter_data[field]
            elif field in data.columns:
                # 如果字段在 data 中，提取该列
                result[field] = data[field]
            else:
                # 如果字段在两个数据源中都不存在，填充为空值
                result[field] = None  # 或者使用 pd.NA、空字符串等

        # 将所有最小下单量为空的填充为0
        result['limit_price_min_vol'] = result['limit_price_min_vol'].astype(float).fillna(0)

        # 将dataframe处理成 class 对象
        result = self.get_instrument_convert_to_instrument(result, instrument_id)

        return result

    @staticmethod
    def get_instrument_convert_to_instrument(df, instrument_id):
        """
        将 DataFrame 转换成 Instrument 对象或对象列表
        :param 用户传入的合约代码
        :param 需要转化的结果 dataframe
        """

        if isinstance(instrument_id, list) and len(instrument_id) > 1:
            # 如果 instrument_id 是列表且长度大于1
            matching_records = df[df['instrument_id'].isin(instrument_id)]
            if matching_records.empty:
                return None  # 没有匹配结果
            else:
                # 去重后返回结果
                unique_records = matching_records.drop_duplicates(subset=['instrument_id'])
                return [Instrument(**row.to_dict()) for _, row in unique_records.iterrows()]
        else:
            # 如果 instrument_id 是单个字符串
            matching_records = df[df['instrument_id'] == instrument_id] if isinstance(instrument_id, str) else df[
                df['instrument_id'].isin(instrument_id)]
            unique_records = matching_records.drop_duplicates(subset=['instrument_id'])
            if matching_records.empty:
                return None  # 没有匹配结果
            elif len(unique_records) == 1:
                return Instrument(**matching_records.iloc[0].to_dict())
            else:
                # 返回匹配结果
                return [Instrument(**row.to_dict()) for _, row in unique_records.iterrows()]

    ''' 查询交易日列表 '''

    def get_trading__dates(self, start_date, end_date, is_include_start=True, is_include_end=True):
        """
        查询交易日列表
        :param start_date: 开始时间
        :param end_date: 结束时间
        :param is_include_start: 是否包含开始时间
        :param is_include_end: 是否包含结束时间
        :return: 交易日列表
        """

        """ 获取数据 """
        if start_date and end_date:
            if not self.validate_dates(start_date, end_date):
                return None
        result, db_session = self.get_trading__dates_get_data(start_date, end_date, is_include_start, is_include_end)
        db_session.close()

        """ 处理返回结果 """
        result = self.get_trading__dates_handle_result(result)

        return result

    def get_trading__dates_get_data(self, start_date, end_date, is_include_start, is_include_end):
        """
        获取交易日历数据
        :param start_date: 开始时间
        :param end_date: 结束时间
        :param is_include_start: 是否包含开始时间
        :param is_include_end: 是否包含结束时间
        :return: 筛选后的交易日历数据
        """

        data, db_session = self.connect_db(trading_dates_db_table_name, trading_dates_db_path)

        # 动态生成比较运算符
        start_operator = ">=" if is_include_start else ">"
        end_operator = "<=" if is_include_end else "<"

        # 构建筛选条件
        filter_condition = f"trading_day {start_operator} {start_date} and trading_day {end_operator} {end_date}"

        # 根据条件筛选数据
        # 筛选 trade_flag 列等于 T 的数据（是交易日的数据）
        filtered_data = data.where(filter_condition).where("trade_flag = 'T'")

        return filtered_data.toDF(), db_session

    @staticmethod
    def get_trading__dates_handle_result(result):
        """
        处理交易日列表成用户要求的格式 ['2024.10.12', '2024.10.13', '2024.10.14']
        :param result: 待处理的交易日历
        :return: 处理后的交易日历
        """

        # 将 trading_day 列转换为指定格式的字符串列表
        return sorted(result['trading_day'].dt.strftime('%Y.%m.%d').tolist())

    """ 查询前/后 N个交易日/时间 """

    def get_trading_date(self, trade_time, date_count, date_type):
        """
        查询前后 N 个交易日或时间点
        :param trade_time: 当前时间点，格式为 'YYYY.MM.DD hh:mm:ss'
        :param date_count: 查询的交易日或时间数量，负数表示向前查询，正数表示向后查询
        :param date_type: 数据类型，'1d' 表示日频率，'1m' 表示分钟频率
        :return: 查询到的交易日或时间点列表
        """
        # 将 trade_time 转换为 datetime 对象
        trade_time = self.format_date(trade_time)

        # 获取交易日历数据
        trading_dates = self.get_trading_dates_data()

        # 定义处理方法映射
        handlers = {
            '1d': self.get_trading_days,
            '1m': self.get_trading_minutes,
        }

        # 根据 date_type 获取对应的处理方法
        handler = handlers.get(date_type)
        if not handler:
            raise ValueError("Invalid date_type. Must be '1d' or '1m'.")

        # 调用对应的处理方法
        return handler(trading_dates, trade_time, date_count)

    def get_trading_dates_data(self):
        """
        获取交易日历数据
        :return: 交易日历数据（DataFrame）
        """
        # 连接数据库并获取数据
        data, db_session = self.connect_db(trading_dates_db_table_name, trading_dates_db_path)
        # 筛选 trade_flag 列等于 T 的数据（是交易日的数据）
        trading_dates = data.where("trade_flag = 'T'").toDF()
        db_session.close()

        # 确保 trading_day 列是 datetime 类型
        trading_dates['trading_day'] = pd.to_datetime(trading_dates['trading_day'])

        return trading_dates

    @staticmethod
    def get_trading_days(trading_dates, trade_time, date_count):
        """
        查询前后 N 个交易日
        :param trading_dates: 交易日历数据
        :param trade_time: 当前时间点
        :param date_count: 查询的交易日数量，负数表示向前查询，正数表示向后查询
        :return: 查询到的交易日列表
        """
        # 筛选 trade_flag 列等于 T 的数据（是交易日的数据）
        trading_dates = trading_dates[trading_dates['trade_flag'] == 'T']

        # 根据 date_count 的正负决定查询方向
        if date_count < 0:
            # 向前查询
            filtered_dates = trading_dates[trading_dates['trading_day'] < trade_time]
            result = filtered_dates['trading_day'].sort_values(ascending=False).head(abs(date_count))
        elif date_count > 0:
            # 向后查询
            filtered_dates = trading_dates[trading_dates['trading_day'] > trade_time]
            result = filtered_dates['trading_day'].sort_values().head(date_count)
        else:
            filtered_dates = trading_dates[trading_dates['trading_day'] == trade_time]
            result = filtered_dates['trading_day']

        # 将结果转换为指定格式的字符串列表
        fina_result = sorted(result.dt.strftime('%Y.%m.%d').tolist())
        return fina_result if len(fina_result) <= 1 else fina_result

    @staticmethod
    def get_trading_minutes(trading_dates, trade_time, date_count):
        """
        查询前后 N 个时间点（仅限交易日）
        :param trading_dates: 交易日历数据
        :param trade_time: 当前时间点
        :param date_count: 查询的时间点数量，负数表示向前查询，正数表示向后查询
        :return: 查询到的时间点列表
        """
        # 确保 trading_dates 的 trading_day 列是 datetime 类型
        trading_dates['trading_day'] = pd.to_datetime(trading_dates['trading_day'])

        # 筛选 trade_flag 列等于 T 的数据（是交易日的数据）
        trading_dates = trading_dates[trading_dates['trade_flag'] == 'T']

        # 转换字符串为 datetime
        trade_time = datetime.datetime.strptime(trade_time, '%Y.%m.%d %H:%M:%S')

        # 生成时间点列表
        time_points = pd.date_range(start=trade_time - datetime.timedelta(minutes=abs(date_count)),
                                    end=trade_time + datetime.timedelta(minutes=abs(date_count)),
                                    freq='min')  # 'T' 表示分钟频率

        def _before_trading_day(_date):
            if _date in trading_dates['trading_day'].dt.date.values:
                return _date
            else:
                _previous_date = _date - datetime.timedelta(days=1)
                return _before_trading_day(_previous_date)

        def _after_trading_day(_date):
            if _date in trading_dates['trading_day'].dt.date.values:
                return _date
            else:
                _previous_date = _date + datetime.timedelta(days=1)
                return _after_trading_day(_previous_date)

        # 将时间点转换为指定格式的字符串
        time_points_str = time_points.strftime('%Y.%m.%d %H:%M:%S')

        # 筛选出在交易日历范围内的时间点
        valid_time_points = []
        for point, point_str in zip(time_points, time_points_str):
            # 检查时间点是否在交易日历中
            if point.date() in trading_dates['trading_day'].dt.date.values:
                valid_time_points.append(point_str)
            else:
                if point.date() < trade_time.date():
                    previous_date = point.date() - datetime.timedelta(days=1)
                    trading_date = _before_trading_day(previous_date)
                elif point.date() > trade_time.date():
                    previous_date = point.date() + datetime.timedelta(days=1)
                    trading_date = _after_trading_day(previous_date)
                else:
                    trading_date = point.date()
                datetime_obj = datetime.datetime.combine(trading_date, datetime.time.min)

                # 获取当天的最后一秒（23:59:59）
                end_of_day = datetime.datetime.combine(datetime_obj.date(), datetime.time(23, 59, 59))
                if trading_date < trade_time.date():
                    _time_points = \
                        pd.date_range(start=end_of_day - datetime.timedelta(minutes=abs(date_count)),
                                      end=end_of_day,
                                      freq='min')
                elif trading_date > trade_time.date():
                    _time_points = \
                        pd.date_range(start=datetime_obj,
                                      end=datetime_obj + datetime.timedelta(minutes=abs(date_count)),
                                      freq='min')
                else:
                    _time_points = \
                        pd.date_range(start=datetime_obj,
                                      end=datetime_obj,
                                      freq='min')
                _time_points = _time_points.strftime('%Y.%m.%d %H:%M:%S')
                valid_time_points.extend(_time_points)

        # 根据 date_count 的正负决定查询方向
        if date_count < 0:
            # 向前查询
            result = [p for p in valid_time_points if pd.to_datetime(p) < trade_time][-abs(date_count):]
        elif date_count > 0:
            # 向后查询
            result = [p for p in valid_time_points if pd.to_datetime(p) > trade_time][:date_count]
        else:
            result = [p for p in valid_time_points if pd.to_datetime(p) == trade_time]

        # return sorted(result) if len(result) > 1 else result[0]
        return sorted(result) if len(result) > 1 else result

    """ 交易日判断 """

    def is_trading_day(self, date):
        """
        判断给定日期是否为交易日
        :param date: 给定日期
        :return: Ture 或 False
        """

        data, db_session = self.connect_db(trading_dates_db_table_name, trading_dates_db_path)
        date = self.format_date(date)

        # 根据条件筛选数据
        # 筛选 trade_flag 列等于 T 的数据（是交易日的数据）
        filtered_data = data.where(f"trading_day = {date}").where("trade_flag = 'T'").toDF()
        db_session.close()

        return False if filtered_data.empty else True

    """ 节假日判断 """

    def is_holiday(self, date):
        """
        判断给定日期是否为节假日
        :param date: 给定的日期
        :return: True 或 False
        """
        date = self.format_date(date)

        # 将输入日期字符串转换为 datetime 对象
        date = datetime.datetime.strptime(date, '%Y.%m.%d').date()
        # 判断是否是节假日
        return calendar.is_holiday(date)

    """ 周末判断 """

    def is_weekend(self, date):
        """
        判断给定日期是否为周末
        :param date: 给定日期
        :return: True 或 False
        """
        date = self.format_date(date)

        # 将输入日期字符串转换为 datetime 对象
        date = datetime.datetime.strptime(date, '%Y.%m.%d')

        # 判断是否是周末（周六或周日）
        return date.weekday() >= 5  # weekday() 返回 5（周六）或 6（周日）
