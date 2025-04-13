from pydantic import BaseModel, Field
from core.model import LanguageModelManager
# from helpers.hotspot_search import get_market_hotspots

from typing import List
from pydantic import BaseModel, Field, conlist

class CompanyEntry(BaseModel):
    """
    A-share listed company entry related to a market hotspot.
    """
    company_name: str = Field(description="Company Name")
    stock_code: str = Field(description="Stock Code (A-share code)")
    association_logic: str = Field(description="Association Logic: Briefly describe how the company's business relates to the hotspot")
    points_of_interest: str = Field(description="Points of Interest: Key points or risks related to the company and hotspot")

class Hotspot(BaseModel):
    """
    Represents a market hotspot with analysis components
    """
    hotspot_board: str = Field(
        description="hotspot or hotspot board"
    )
    core_news: str = Field(
        description="Key news event or information driving the hotspot"
    )
    driving_factors_analysis: str = Field(
        description="Analysis of reasons and background for the hotspot's formation"
    )
    short_term_impact: str = Field(
        description="Analysis of potential short-term market impacts from the hotspot"
    )
    medium_term_impact: str = Field(
        description="Analysis of potential medium-term market impacts from the hotspot"
    )
    related_companies: List[CompanyEntry] = Field(
        ...,
        description="List of related A-share companies with detailed information"
    )

class MarketHotspotAnalysis(BaseModel):
    """
    Market analysis containing multiple hotspots with comprehensive analysis
    """
    hotspots: list[Hotspot] = Field(
        ...,
        description="List containing at least two market hotspot sectors or themes for analysis"
    )

llm = LanguageModelManager().get_models()["llm_oai_o3"]

structured_llm = llm.with_structured_output(MarketHotspotAnalysis)

def structure_output(content):
    result = structured_llm.invoke(content)
    # 返回json
    
    return result.model_dump()
if __name__ == "__main__":
    content = """
 **低空经济**】
核心新闻: 地方政策持续加码，如上海、深圳、合肥等地积极行动，营造良好发展环境；中央空管委宣布在六个城市开展eVTOL（电动垂直起降飞行器）试点，标志着低空经济进入新的发展阶段；企业层面，亿航智能的无人驾驶载人航空器运营合格证（OC证）申请获民航局受理，有望年内获批进入商业化运营；小鹏汇天“陆地航母”飞行汽车启动预售。
驱动因素分析:
*   **政策密集出台:** 从中央到地方，支持低空经济发展的政策频繁落地，明确了其战略性新兴产业的地位，并提供了发展指引和支持措施。
*   **技术突破与应用加速:** eVTOL、无人机等关键技术不断取得进展，商业化应用场景（如物流、载人交通、应急救援）逐渐清晰并开始落地。
*   **市场空间广阔:** 机构普遍预测低空经济将形成万亿级市场规模，巨大的发展潜力吸引了各类资本和企业的积极布局。
市场影响推演:
*   短期: 政策利好和试点城市的确定持续刺激市场情绪，相关概念股活跃度较高，但需注意部分个股前期涨幅较大，存在波动风险。技术突破和商业化进展（如亿航智能OC证获批）可能带来阶段性行情。
*   中期: 随着基础设施建设（如空域管理、起降点）、法规标准完善以及更多eVTOL型号通过适航认证，低空经济将逐步从概念走向实际应用和商业化运营。产业链相关公司（如飞行器制造、核心零部件、运营服务、基础设施）的业绩有望逐步兑现，但产业发展速度和商业模式成熟度仍需观察。

| 股票名称   | 股票代码   | 关联逻辑                                                     | 关注要点                                                     |
| :--------- | :--------- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| 亿航智能   | EH (美股)  | 全球领先的eVTOL公司，EH216-S已获型号合格证（TC）和生产许可证（PC），运营合格证（OC）申请已获受理。 | 商业化运营进展、订单交付情况、OC证获批时间点、固态电池合作进展。 |
| 万丰奥威   | 002085     | 公司与战略合作方在eVTOL领域有深入布局，其通航飞机制造业务具备协同优势。 | eVTOL项目具体进展、合作模式、通航业务发展。                  |
| 中无人机   | 688297     | 国内军用无人机龙头企业之一，在无人机领域技术积累深厚。       | 技术在民用低空经济领域的拓展应用、订单情况。                 |
| 纵横股份   | 688070     | 工业无人机领先企业，产品应用于测绘、巡检等多个低空场景。     | 工业无人机市场需求、新产品研发、下游应用拓展。             |
| 莱斯信息   | 688631     | 提供空管系统解决方案，有望受益于低空空域管理基础设施建设。   | 低空空管系统订单获取情况、技术研发进展。                   |
| 深城交     | 301091     | 参与深圳等地的低空智能融合基础设施项目建设。                 | 参与低空基建项目的中标和实施情况。                         |

【**固态电池**】
核心新闻: 近期多家车企（如比亚迪、广汽、长安）和电池厂商公布固态电池（含半固态）研发进展和量产时间表（多集中在2026-2027年左右启动装车应用）；华为、比亚迪等公布固态电池相关专利；中国全固态电池产学研协同创新平台年会等行业会议召开，讨论产业进展。
驱动因素分析:
*   **能量密度与安全性需求:** 现有液态锂电池能量密度接近理论上限，固态电池在高能量密度和高安全性方面具有显著优势，被视为下一代电池技术的重要方向。
*   **产业化进程加速预期:** 主流车企和电池厂纷纷给出量产时间表，虽然距离大规模应用尚有时日，但产业化预期明显提前，带动了市场对相关技术和产业链的关注。
*   **技术路线多样化:** 氧化物、硫化物、聚合物等多种固态电解质路线并行发展，相关材料、设备企业积极布局。
市场影响推演:
*   短期: 技术进展、专利发布、企业合作等消息容易引发市场对概念股的炒作，板块波动性较大。需关注技术突破的真实性和量产的可行性。
*   中期: 固态电池（尤其是半固态电池）有望率先在高端车型、消费电子、eVTOL等领域实现小批量应用。产业链中具备核心技术和量产能力的企业将率先受益，包括电解质材料、负极材料（如硅基负极、锂金属负极）、设备等环节。全固态电池的商业化仍面临成本、工艺成熟度等多重挑战。

| 股票名称   | 股票代码   | 关联逻辑                                                     | 关注要点                                                     |
| :--------- | :--------- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| 宁德时代   | 300750     | 动力电池龙头，已发布凝聚态电池（属半固态范畴），并在固态电池领域有深厚技术储备。 | 凝聚态电池量产及装车进展、固态电池研发投入与突破。         |
| 比亚迪     | 002594     | 新能源汽车和电池巨头，计划在2027年左右启动全固态电池批量示范装车应用。 | 固态电池研发进度、专利布局、量产时间表的兑现情况。         |
| 赣锋锂业   | 002460     | 锂业龙头，布局固态锂电池研发和生产。                         | 固态电池项目进展、产能规划、技术路线选择。                 |
| 恩捷股份   | 002812     | 隔膜龙头，固态电池可能改变隔膜需求，公司也在关注和布局相关技术。 | 固态电池对现有隔膜市场的影响、公司在固态电池隔膜或涂覆材料方面的布局。 |
| 当升科技   | 300073     | 正极材料领先企业，积极研发适配固态电池的高性能正极材料。     | 固态电池正极材料的研发进展、客户验证情况。                 |
| 贝特瑞     | 835185     | 负极材料龙头，其硅基负极、锂金属负极等产品可用于固态/半固态电池。 | 适用于固态电池的负极材料研发、客户导入及量产情况。         |
| 上海洗霸   | 603200     | 与中科院上海硅酸盐研究所合作，布局固态电解质材料研发生产。   | 固态电解质粉体材料的性能、量产进展、下游客户合作。         |
| 先导智能   | 300450     | 锂电设备龙头，提供固态电池相关生产设备。                     | 固态电池设备订单获取情况、技术研发能力。                   |
"""
    print(structure_output(content))