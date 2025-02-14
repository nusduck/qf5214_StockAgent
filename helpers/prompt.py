def make_system_prompt(suffix: str) -> str:
    return (
        "You are a helpful AI assistant, collaborating with other assistants."
        " Use the provided tools to progress towards answering the question."
        " If you are unable to fully answer, that's OK, another assistant with different tools "
        " will help where you left off. Execute what you can to make progress."
        " If you or any of the other assistants have the final answer or deliverable,"
        " prefix your response with FINAL ANSWER so the team knows to stop."
        f"\n{suffix}"
    )
data_collect_prompt = f"""
根据你的信息获取给定公司在中国股市的6位股票代码，利用所有的工具来获取各项数据。
"""
hot_spot_search_prompt = """请使用英语或者中文搜索总结过去一周中国大陆金融市场热点事件及相关上市公司，要求：
1. 首先用1-2段文字进行总体归纳
2. 使用规范的Markdown表格呈现，必须包含以下列：
   - 股票代码（格式示例：600000.SH/00700.HK）
   - 公司全称
   - 相关事件（说明具体事件及其影响）
   - 信息源（提供可点击的完整新闻链接）
3. 确保：
   - 所有信息基于公开可信来源（如公司公告、上交所/深交所披露、权威财经媒体）
   - 股票代码准确且包含交易所后缀
   - 事件描述清晰简明
   - 每个条目必须提供至少一个信息源链接"""

if __name__ == "__main__":
    print(make_system_prompt("What is the capital of France?"))