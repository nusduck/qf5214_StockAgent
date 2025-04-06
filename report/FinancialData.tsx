'use client';

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface FinancialDataProps {
  data: any;
}

const FinancialData = ({ data }: FinancialDataProps) => {
  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>财务数据</CardTitle>
      </CardHeader>
      <CardContent>
        {data && typeof data === 'object' ? (
          <div className="space-y-4">
            <div className="bg-muted rounded-md p-4">
              <div className="space-y-2">
                {Object.entries(data).map(([key, value]) => (
                  <div key={key} className="text-sm">
                    <span className="font-medium">{key}:</span> {JSON.stringify(value)}
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">暂无财务数据</p>
        )}
      </CardContent>
    </Card>
  );
};

export default FinancialData; 