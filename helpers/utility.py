from langchain_core.messages import  ToolMessage
def extract_specific_tool_message(messages, tool_name=None, tool_call_id=None):
    """
    从messages中提取指定工具的消息
    """
    for message in messages:
        if isinstance(message, ToolMessage):
            if tool_name and message.name == tool_name:
                return message
            if tool_call_id and message.tool_call_id == tool_call_id:
                return message
    return None #如果找不到，返回None