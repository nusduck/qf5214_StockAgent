import akshare as ak
import pandas as pd

def get_stock_sector_data(sector: str) -> pd.DataFrame:
    """
    获取指定股票板块的相关数据，并按表格格式返回。

    参数：
    sector (str): 股票板块名称（如 "银行"、"新能源"）

    返回：
    pd.DataFrame: 股票板块的相关数据表
    """
    # 获取所有行业板块数据（使用 stock_board_industry_name_em）
    try:
        sector_list = ak.stock_board_industry_name_em()
    except Exception as e:
        raise ValueError(f"无法获取行业板块列表。错误：{str(e)}")

    # 检查板块是否存在
    if sector not in sector_list["板块名称"].values:
        raise ValueError(f"无法找到名为 {sector} 的板块，请检查板块名称是否正确。")
    
    # 获取指定板块的成分股数据（使用 stock_board_industry_cons_em）
    try:
        sector_data = ak.stock_board_industry_cons_em()
    except Exception as e:
        raise ValueError(f"无法获取 {sector} 板块的成分股数据。错误：{str(e)}")

    # 打印 sector_data，检查实际列名
    print(sector_data.head())  # 查看返回的数据框的前几行

    if sector_data.empty:
        raise ValueError(f"无法获取 {sector} 板块的成分股数据，请检查板块名称是否正确。")

    # 假设数据中包含 '代码' 列（根据实际打印出来的列名调整）
    stock_data_list = []
    for symbol in sector_data["代码"]:  # 使用实际列名来替代 '品种代码'
        data = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq", start_date="20230101", end_date="20230201")
        if not data.empty:
            last_data = data.iloc[-1]
            prev_close = data.iloc[-2]["收盘"] if len(data) > 1 else last_data["收盘"]  # 如果没有前一交易日的数据，则使用最新数据
            
            # 计算涨跌幅和涨跌额
            change = last_data["收盘"] - prev_close
            change_percent = (change / prev_close) * 100

            stock_data = {
                "股票代码": [symbol],
                "股票名称": [sector_data[sector_data["代码"] == symbol]["名称"].values[0]],  # 根据实际列名调整
                "日期时间": [last_data["日期"]],
                "开盘": [last_data["开盘"]],
                "收盘": [last_data["收盘"]],
                "最高": [last_data["最高"]],
                "最低": [last_data["最低"]],
                "涨跌幅": [round(change_percent, 2)],  # 单位 %
                "涨跌额": [round(change, 2)],
                "成交量": [int(last_data["成交量"])],  # 成交量
                "成交额": [round(last_data["成交额"], 2)],  # 成交金额
                "振幅": [round(last_data["振幅"], 2)],  # 单位 %
                "换手率": [round(last_data["换手率"], 2)]  # 换手率（%）
            }

            stock_data_list.append(stock_data)

    # 合并所有股票数据
    result_df = pd.DataFrame(stock_data_list[0]) if stock_data_list else pd.DataFrame()
    for stock_data in stock_data_list[1:]:
        result_df = pd.concat([result_df, pd.DataFrame(stock_data)], ignore_index=True)

    return result_df

# 示例调用
sector = "银行"  # 例如查询银行板块
df = get_stock_sector_data(sector)
print(df)
