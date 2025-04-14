'use client'

import {useState, useEffect} from 'react'
import {Button, Skeleton, Card, Tabs, Table, Badge, Empty, Alert, Spin} from 'antd'
import {ReloadOutlined, StockOutlined, BarChartOutlined, InfoCircleOutlined} from '@ant-design/icons'
import styles from '../styles/recommendation.module.css'
import type {TabsProps} from 'antd'
import type {ColumnsType} from 'antd/es/table'

interface Company {
  company_name: string
  stock_code: string
  association_logic: string
  points_of_interest: string
}

interface Hotspot {
  hotspot_board: string
  core_news: string
  driving_factors_analysis: string
  short_term_impact: string
  medium_term_impact: string
  related_companies: Company[]
}

interface HotspotData {
  hotspots: Hotspot[]
}

export default function RecommendationPage() {
  const [hotspotData, setHotspotData] = useState<HotspotData | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState('')
  const [activeHotspotTab, setActiveHotspotTab] = useState('0')

  const stockColumns: ColumnsType<Company> = [
    {
      title: '公司名称',
      dataIndex: 'company_name',
      key: 'company_name',
      width: 120,
      render: (text) => <strong style={{ color: "#ffffff" }}>{text}</strong>
    },
    {
      title: '股票代码',
      dataIndex: 'stock_code',
      key: 'stock_code',
      width: 140,
      render: (text) => <span className={styles.stockCode}>{text}</span>
    },
    {
      title: '关联逻辑',
      dataIndex: 'association_logic',
      key: 'association_logic',
      className: styles.descriptionColumn,
    },
    {
      title: '关注要点',
      dataIndex: 'points_of_interest',
      key: 'points_of_interest',
      className: styles.descriptionColumn,
    }
  ]

  const fetchHotspotData = async (forceRefresh = false) => {
    try {
      setRefreshing(true)
      // 确保路径与后端API匹配
      const url = forceRefresh 
        ? `/api/hotspots?force_refresh=true` 
        : `/api/hotspots`
      
      console.log("正在请求热点数据:", url)
      const res = await fetch(url)
      
      if (!res.ok) {
        console.error("请求失败:", res.status, res.statusText)
        throw new Error(`HTTP error! Status: ${res.status}`)
      }
      
      const data = await res.json()
      console.log("获取到数据:", data)
      
      if (data?.data?.hotspots) {
        setHotspotData(data.data)
        setError('')
      } else {
        console.error("数据结构异常:", data)
        setError('返回数据结构异常')
      }
    } catch (err: any) {
      console.error("请求异常:", err)
      setError('接口请求失败: ' + (err.message || '未知错误'))
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchHotspotData()
  }, [])

  const onRefresh = () => {
    fetchHotspotData(true)
  }

  // 根据热点数据生成Tabs配置
  const generateHotspotTabs = () => {
    if (!hotspotData || !hotspotData.hotspots) return []
    
    return hotspotData.hotspots.map((hotspot, index) => ({
      key: index.toString(),
      label: (
        <span className={styles.tabLabel}>
          <StockOutlined />
          {hotspot.hotspot_board}
        </span>
      ),
      children: (
        <div className={styles.hotspotTabContent}>
          <HotspotDetail hotspot={hotspot} />
        </div>
      )
    }))
  }

  // 热点详情组件
  const HotspotDetail = ({hotspot}: {hotspot: Hotspot}) => (
    <div className={styles.hotspotDetail}>
      <div className={styles.hotspotSection}>
        <h3 className={styles.sectionTitle}>
          <Badge status="processing" text={<span style={{ color: "#ffffff" }}>核心新闻</span>} />
        </h3>
        <div className={styles.sectionContent}>{hotspot.core_news}</div>
      </div>
      
      <div className={styles.hotspotSection}>
        <h3 className={styles.sectionTitle}>
          <Badge status="success" text={<span style={{ color: "#ffffff" }}>驱动因素分析</span>} />
        </h3>
        <div className={styles.sectionContent}>{hotspot.driving_factors_analysis}</div>
      </div>
      
      <div className={styles.impactSection}>
        <div className={styles.impactItem}>
          <h3 className={styles.sectionTitle}>
            <Badge status="warning" text={<span style={{ color: "#ffffff" }}>短期影响</span>} />
          </h3>
          <div className={styles.sectionContent}>{hotspot.short_term_impact}</div>
        </div>
        
        <div className={styles.impactItem}>
          <h3 className={styles.sectionTitle}>
            <Badge status="default" text={<span style={{ color: "#ffffff" }}>中期影响</span>} /> 
          </h3>
          <div className={styles.sectionContent}>{hotspot.medium_term_impact}</div>
        </div>
      </div>
      
      <div className={styles.stocksTableSection}>
        <h3 className={styles.sectionTitle}>
          <Badge status="error" text={<span style={{ color: "#ffffff" }}>相关股票</span>} />
        </h3>
        <Table 
          dataSource={hotspot.related_companies} 
          columns={stockColumns} 
          rowKey="company_name"
          pagination={false}
          size="small"
          className={styles.stocksTable}
        />
      </div>
    </div>
  )

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>
          <BarChartOutlined className={styles.titleIcon} />
          市场热点分析报告
        </h1>
        <Button 
          type="primary" 
          style={{ background: "#9c27b0", borderColor: "#9c27b0" }}
          icon={<ReloadOutlined spin={refreshing} />} 
          onClick={onRefresh}
          loading={refreshing}
          className={styles.refreshButton}
        >
          刷新分析
        </Button>
      </div>
      
      {error && (
        <Alert
          message="加载失败"
          description={error}
          type="error"
          showIcon
          className={styles.errorAlert}
          action={
            <Button size="small" danger onClick={onRefresh}>
              重试
            </Button>
          }
        />
      )}
      
      <div className={styles.content}>
        {loading ? (
          <div className={styles.loadingContainer}>
            <Card>
              <Skeleton active paragraph={{ rows: 10 }} />
            </Card>
          </div>
        ) : hotspotData && hotspotData.hotspots?.length > 0 ? (
          <Tabs
            defaultActiveKey="0"
            activeKey={activeHotspotTab}
            onChange={setActiveHotspotTab}
            className={styles.hotspotTabs}
            items={generateHotspotTabs() as TabsProps['items']}
          />
        ) : (
          <Empty
            description="暂无热点数据"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        )}
      </div>
      
      {!loading && !error && hotspotData && (
        <div className={styles.footer}>
          <div className={styles.disclaimer}>
            <InfoCircleOutlined /> 免责声明：本分析仅供参考，不构成投资建议。投资有风险，入市需谨慎。
          </div>
        </div>
      )}
    </div>
  )
}
