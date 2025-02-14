from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

# from helpers.prompt import hot_spot_search_prompt

def get_market_hotspots():
    client = genai.Client()
    model_id = "gemini-2.0-flash"

    google_search_tool = Tool(
        google_search = GoogleSearch()
    )

    response = client.models.generate_content(
        model=model_id,
        contents="Chinese mainland financial market last week hotspot and the related listed company and their stock code you can search in Chinese return with table format please.",
        config=GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        )
    )
    
    result_text = ""
    for candidate in response.candidates:
        for part in candidate.content.parts:
            result_text += part.text + "\n"
    
    return result_text

# 如果直接运行此文件，则执行测试
if __name__ == "__main__":
    print(get_market_hotspots())
