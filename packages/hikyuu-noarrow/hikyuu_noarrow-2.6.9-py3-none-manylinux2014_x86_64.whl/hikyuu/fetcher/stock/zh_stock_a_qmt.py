#!/usr/bin/python
# -*- coding: utf8 -*-
#
# Create on: 2024-08-22
#    Author: fasiondog

from hikyuu import Datetime
from hikyuu.util import *

try:
    from xtquant import xtdata

    @hku_catch(trace=True, callback=lambda stk: hku_warn("Failed parse stk: {}", stk))
    def parse_one_result_qmt(stk_code: str, data: dict):
        '''将 qmt tick 数据转为 spot 数据

        :param str stk_code: qmt 风格的证券编码，如 000001.SZ
        :param dict data: 对应的 qmt 全推 tick 数据
        '''
        result = {}
        code, market = stk_code.split('.')
        result['market'] = market
        result['code'] = code
        result['name'] = ''
        result['datetime'] = Datetime(data['timetag']) if 'timetag' in data else xtdata.timetag_to_datetime(
            data['time'], "%Y-%m-%d %H:%M:%S")

        result['yesterday_close'] = data['lastClose']
        result['open'] = data['open']
        result['high'] = data['high']
        result['low'] = data['low']
        result['close'] = data['lastPrice']
        result['amount'] = data['amount'] * 0.0001  # 转千元
        result['volume'] = data['pvolume'] * 0.01  # 转手数

        result['bid'] = data['bidPrice']
        result['bid_amount'] = data['bidVol']
        result['ask'] = data['askPrice']
        result['ask_amount'] = data['askVol']
        return result

    def get_spot(stocklist, unused1=None, unused2=None, batch_func=None):
        code_list = [f'{s.code}.{s.market}' for s in stocklist]
        full_tick = xtdata.get_full_tick(code_list)
        records = [parse_one_result_qmt(code, data) for code, data in full_tick.items()]
        if batch_func is not None:
            batch_func(records)
        return records

except:
    def parse_one_result_qmt(stk_code: str, data: dict):
        hku_error("Not fount xtquant")
        return dict()

    def get_spot(stocklist, unused1=None, unused2=None, batch_func=None):
        hku_error("Not fount xtquant")
        return list()
