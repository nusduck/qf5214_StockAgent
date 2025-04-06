'use client';

import React, { useEffect } from "react";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ReportModuleProps {
  basicData: any;
  marketData: any;
  financialData: any;
  researchData: any;
}

const ReportModule: React.FC<ReportModuleProps> = ({ 
  basicData, 
  marketData, 
  financialData, 
  researchData 
}) => {
  useEffect(() => {
    // 调试日志 - 查看接收到的数据
    console.log("===== 报告模块数据 =====");
    console.log("基本数据:", basicData);
    
    // 检查report_state是否存在
    if (basicData?.report_state) {
      console.log("报告状态:", basicData.report_state);
      
      // 检查text_reports字段，可能在report_state直接层级或下一级
      const textReports = basicData.report_state.text_reports || basicData.report_state;
      console.log("文本报告:", textReports);
      
      if (textReports) {
        // 尝试找出报告包含的部分
        const reportKeys = Object.keys(textReports).filter(key => 
          typeof textReports[key] === 'string' && 
          textReports[key].length > 0
        );
        
        console.log("报告包含的部分:", reportKeys.join(", "));
        
        // 打印每个报告的长度
        reportKeys.forEach(key => {
          console.log(`${key} 长度:`, textReports[key].length);
        });
      }
    }
  }, [basicData, marketData, financialData, researchData]);

  // 检查是否所有数据都已加载
  if (!basicData) {
    return (
      <div className="p-8 text-center">
        <Alert>
          <AlertTitle>需要加载基础数据</AlertTitle>
          <AlertDescription>
            请先加载基础数据，然后返回查看综合报告
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // 获取报告数据，可能在不同的嵌套层级
  let reportState = basicData.report_state;
  let textReports: Record<string, string> = {};
  
  // 灵活查找报告文本数据位置
  if (reportState) {
    // 情况1: text_reports在report_state下
    if (reportState.text_reports && typeof reportState.text_reports === 'object') {
      textReports = reportState.text_reports;
    } 
    // 情况2: report_state本身就包含报告数据
    else if (typeof reportState === 'object') {
      // 查找键名以_report结尾的字段，通常是报告数据
      Object.keys(reportState).forEach(key => {
        if (key.endsWith('_report') && typeof reportState[key] === 'string') {
          textReports[key] = reportState[key];
        }
      });
    }
  }
  
  // 如果找不到报告数据
  if (Object.keys(textReports).length === 0) {
    return (
      <div className="p-8 text-center">
        <Alert>
          <AlertTitle>暂无报告数据</AlertTitle>
          <AlertDescription>
            未找到有效的报告数据，请尝试重新分析
          </AlertDescription>
        </Alert>
      </div>
    );
  }
  
  // 定义报告类型及显示名称
  const reportTypes = [
    { key: 'fundamentals_report', title: '基本面分析', bgClass: 'bg-indigo-100 dark:bg-indigo-800 text-indigo-900 dark:text-indigo-50' },
    { key: 'fundamental_report', title: '基本面分析', bgClass: 'bg-indigo-100 dark:bg-indigo-800 text-indigo-900 dark:text-indigo-50' },  // 兼容另一种命名
    { key: 'technical_report', title: '技术面分析', bgClass: 'bg-blue-100 dark:bg-blue-800 text-blue-900 dark:text-blue-50' },
    { key: 'sentiment_report', title: '市场情绪分析', bgClass: 'bg-green-100 dark:bg-green-800 text-green-900 dark:text-green-50' },
    { key: 'sentiment', title: '市场情绪分析', bgClass: 'bg-green-100 dark:bg-green-800 text-green-900 dark:text-green-50' },  // 兼容另一种命名
    { key: 'adversarial_report', title: '综合评估', bgClass: 'bg-amber-100 dark:bg-amber-800 text-amber-900 dark:text-amber-50' }
  ];
  
  // 自定义Markdown组件样式
  const markdownComponents = {
    h1: (props: any) => <h1 className="text-xl font-bold my-4 text-gray-900 dark:text-gray-100" {...props} />,
    h2: (props: any) => <h2 className="text-lg font-bold mt-6 mb-3 pb-1 border-b border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100" {...props} />,
    h3: (props: any) => <h3 className="text-md font-bold mt-4 mb-2 text-gray-900 dark:text-gray-100" {...props} />,
    h4: (props: any) => <h4 className="text-md font-semibold mt-3 mb-2 text-gray-900 dark:text-gray-100" {...props} />,
    h5: (props: any) => <h5 className="text-sm font-semibold mt-3 mb-1 text-gray-900 dark:text-gray-100" {...props} />,
    ul: (props: any) => <ul className="list-disc ml-5 my-2 space-y-1 text-gray-800 dark:text-gray-200" {...props} />,
    ol: (props: any) => <ol className="list-decimal ml-5 my-2 space-y-1 text-gray-800 dark:text-gray-200" {...props} />,
    li: (props: any) => <li className="mb-1 text-gray-800 dark:text-gray-200" {...props} />,
    p: (props: any) => <p className="my-2 text-gray-800 dark:text-gray-200" {...props} />,
    a: (props: any) => <a className="text-blue-600 dark:text-blue-400 hover:underline" {...props} />,
    strong: (props: any) => <strong className="font-bold text-gray-900 dark:text-gray-100" {...props} />,
    em: (props: any) => <em className="italic text-gray-800 dark:text-gray-200" {...props} />,
    blockquote: (props: any) => <blockquote className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 my-2 italic text-gray-700 dark:text-gray-300" {...props} />,
    code: (props: any) => <code className="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-gray-800 dark:text-gray-200" {...props} />,
    pre: (props: any) => <pre className="bg-gray-100 dark:bg-gray-800 p-3 rounded my-3 overflow-auto text-gray-800 dark:text-gray-200" {...props} />,
    table: (props: any) => <table className="min-w-full divide-y divide-gray-300 dark:divide-gray-700 my-4 text-gray-800 dark:text-gray-200" {...props} />,
    th: (props: any) => <th className="px-3 py-2 bg-gray-50 dark:bg-gray-800 text-left text-xs font-medium uppercase tracking-wider text-gray-700 dark:text-gray-300" {...props} />,
    td: (props: any) => <td className="px-3 py-2 whitespace-nowrap text-gray-800 dark:text-gray-200" {...props} />,
    tr: (props: any) => <tr className="border-b border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-200" {...props} />,
    hr: (props: any) => <hr className="my-4 border-gray-300 dark:border-gray-700" {...props} />
  };
  
  return (
    <div className="space-y-6">
      <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-md shadow-sm">
        <h3 className="text-lg font-bold mb-2 text-gray-900 dark:text-gray-100">{basicData.stock_name} ({basicData.stock_code}) - 分析总结</h3>
        <p className="mb-4 text-gray-700 dark:text-gray-300">行业: {basicData.industry}</p>
        
        {/* 显示报告内容 */}
        <div className="space-y-8">
          {reportTypes.map(type => (
            textReports[type.key] && (
              <div key={type.key} className="border border-gray-200 dark:border-gray-700 rounded-md overflow-hidden shadow-sm">
                <h4 className={`text-md font-medium ${type.bgClass} p-3`}>{type.title}</h4>
                <div className="p-4 text-sm bg-white dark:bg-gray-900 overflow-auto max-h-[600px] text-gray-900 dark:text-gray-100">
                  {React.createElement(ReactMarkdown, {
                    components: markdownComponents,
                    children: textReports[type.key],
                    remarkPlugins: [remarkGfm]
                  })}
                </div>
              </div>
            )
          ))}
          
          <div className="mt-6 text-xs text-gray-500 dark:text-gray-400">
            <p>免责声明：本报告仅供参考，不构成任何投资建议。投资有风险，入市需谨慎。</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportModule;