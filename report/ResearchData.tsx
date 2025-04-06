'use client';

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useResearchData } from '@/hooks/useResearchData';
import { formatDate } from '@/lib/utils';

interface ResearchDataProps {
  data: {
    analyst_data: any;
    news_data: string[];
  };
}

const ResearchData = ({ data }: ResearchDataProps) => {
  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>研究报告</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {data.analyst_data && (
            <div>
              <h3 className="text-sm font-medium mb-2">分析师观点</h3>
              <div className="bg-muted rounded-md p-4">
                {typeof data.analyst_data === 'object' ? (
                  <div className="space-y-2">
                    {Object.entries(data.analyst_data).map(([key, value]) => (
                      <div key={key} className="text-sm">
                        <span className="font-medium">{key}:</span> {JSON.stringify(value)}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm">{JSON.stringify(data.analyst_data)}</p>
                )}
              </div>
            </div>
          )}
          
          {data.news_data && data.news_data.length > 0 && (
            <div>
              <h3 className="text-sm font-medium mb-2">相关新闻</h3>
              <ul className="space-y-2 bg-muted rounded-md p-4">
                {data.news_data.map((news, index) => (
                  <li key={index} className="text-sm">• {news}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ResearchData; 