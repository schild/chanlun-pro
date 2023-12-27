from jqdata import *
import cl
import datetime
import pandas as pd


# 获取市值前几的股票列表
def stock_market_cap(num):
    df = get_fundamentals(query(valuation.code, valuation.market_cap).filter(
        valuation.market_cap > num
    ).order_by(
        # 按市值降序排列
        valuation.market_cap.desc()
    ), date=None)
    stocks = []
    for d in df.iterrows():
        s = get_security_info(d[1]['code'])
        stocks.append({'code': d[1]['code'], 'name': s.display_name})
    return stocks


# 获取指定周期的缠论数据
def get_cl_datas(code, frequencys, cl_config):
    klines = {}
    for f in frequencys:
        _k = get_bars(code, 2000, unit=f, fields=['date', 'open', 'high', 'low', 'close', 'volume'], include_now=True,
                      end_dt=None, df=True)
        _k['code'] = code
        _k = _k[['code', 'date', 'open', 'close', 'high', 'low', 'volume']]
        _k['date'] = pd.to_datetime(_k['date'])
        klines[f] = _k
    return cl.web_batch_get_cl_datas(code, klines, cl_config)


# 格式化代码与富途的统一
def reformat_code(code):
    if isinstance(code, list):
        return [reformat_code(c) for c in code]
    symbol = code[:6]
    exchange = code[-5:]
    return 'SH.' + symbol if exchange == '.XSHG' else 'SZ.' + symbol


def stock_names(codes):
    names = []
    for code in codes:
        stock = get_security_info(code)
        names.append(stock.display_name)
    return names


# 获取股票行业信息
def stock_hys(code):
    # 股票的行业信息
    stock_industrys = get_industry(security=[code])
    hy = stock_industrys[code]
    return '--' if 'jq_l2' not in hy else hy['jq_l2']['industry_name']


# 获取股票概念信息
def stock_gns(code):
    # 股票的概念信息
    stock_concepts = get_concept(code, date=datetime.date.today())
    gn = ''.join(
        co['concept_name'] + ' / ' for co in stock_concepts[code]['jq_concept']
    )
    return gn[:-3]


def stock_jj_bx_share_ok(code):
    # 查询前十大流通股中，基金占比，需要大于 2%
    lt_top10 = finance.run_query(query(finance.STK_SHAREHOLDER_FLOATING_TOP10).filter(
        finance.STK_SHAREHOLDER_FLOATING_TOP10.code == code).order_by(
        finance.STK_SHAREHOLDER_FLOATING_TOP10.end_date.desc()).limit(10))
    jj_share_ratio = 0
    for lt in lt_top10.iterrows():
        shareholder_class = lt[1]['shareholder_class']
        if shareholder_class == '证券投资基金':
            share_ratio = lt[1]['share_ratio']
            jj_share_ratio += share_ratio
    if jj_share_ratio >= 2:
        return True

    # 查询北向持股大于 3000万
    link_id = 310001 if 'XSHG' in code else 310002
    bx = finance.run_query(query(finance.STK_HK_HOLD_INFO).filter(finance.STK_HK_HOLD_INFO.link_id == link_id,
                                                                  finance.STK_HK_HOLD_INFO.code == code).order_by(
        finance.STK_HK_HOLD_INFO.day.desc()).limit(1))
    price = get_ticks(code, end_dt=datetime.datetime.now(), fields=['current'], count=1)
    price = price[0][0]
    share_balance = bx.iloc[0]['share_number'] * price if len(bx) == 1 else 0
    return share_balance >= 30000000


def get_mla_buy_point(cd_w: cl.CL, cd_d: cl.CL, cd_30m: cl.CL):
    if len(cd_d.bis) == 0:
        return None
    bi_d = cd_d.bis[-1]
    if len(bi_d.line_mmds()) == 0 or 'buy' not in '.'.join(bi_d.line_mmds()):
        return None
    if cd_d.cl_klines[-1].index - bi_d.end.k.index > 2:
        return None
    mla = cl.MultiLevelAnalyse(cd_d, cd_30m)
    low_qs = mla.up_bi_low_level_qs()
    bi_30m = low_qs['low_last_bi']
    if bi_30m is None:
        return None

    if low_qs['zs_num'] >= 1 or low_qs['qs_done'] or bi_30m.bc_exists(['pz', 'qs']):
        return f"{cd_d.frequency} 级别 {bi_d.line_mmds()} 买点，{cd_30m.frequency} 级别趋势（中枢 {low_qs['zs_num']} 完成 {low_qs['qs_done']} 趋势背驰 {bi_30m.bc_exists(['qs'])} 盘整背驰 {bi_30m.bc_exists(['pz'])}）"

    return None


def get_week_day_buy(cd_w: cl.CL, cd_d: cl.CL):
    """
    查询 周 和 日 线级别有买点，并且 周线的 macd 线在 零轴之上
    """
    if len(cd_w.bis) == 0 or len(cd_d.bis) == 0:
        return None

    if cd_w.idx['macd']['dif'][-1] < 0 or cd_w.idx['macd']['dea'][-1] < 0:
        return None
    bi_w = cd_w.bis[-1]
    bi_d = cd_d.bis[-1]

    check_buys = ['1buy', '2buy', 'l2buy', '3buy', 'l3buy']
    return (
        f'{cd_w.frequency} 级别 {bi_w.line_mmds()} 买点，{cd_d.frequency} 级别 {bi_d.line_mmds()} 买点'
        if bi_w.mmd_exists(check_buys) and bi_d.mmd_exists(check_buys)
        else None
    )


def get_buy_point(cd: cl.CL):
    """
    查询日线有买点的股票
    """
    if len(cd.bis) == 0:
        return None
    bi = cd.bis[-1]

    if bi.mmd_exists(['1buy', '2buy', 'l2buy', '3buy', 'l3buy']):
        return f'出现买点 {bi.line_mmds()}'
    return None


def get_xd_buy_and_bc(cd: cl.CL):
    """
    查询线段买点，并且笔有盘整背驰
    """
    if len(cd.xds) == 0 or len(cd.bis) == 0:
        return None
    bi = [_bi for _bi in cd.bis if _bi.type == 'down'][-1]
    xd = cd.xds[-1]

    if len(xd.line_mmds()) > 0 and (xd.bc_exists(['xd', 'pz', 'qs']) or bi.bc_exists(['qs', 'pz'])):
        return f' {cd.frequency}级别 出现线段买点（{xd.line_mmds()} / {xd.line_bcs()}）并且笔背驰（{bi.line_bcs()}）'
    return None
