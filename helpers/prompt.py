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
if __name__ == "__main__":
    print(make_system_prompt("What is the capital of France?"))