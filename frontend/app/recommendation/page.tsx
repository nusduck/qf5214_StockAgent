'use client';

import { Suspense } from 'react';
import { useStockData } from '../../hooks/useStockData';
import { StockList } from '../../components/StockList';
import Loading from './loading';

export default function RecommendationPage() {
  return (
    <div className="min-h-screen bg-gray-900">
      <div className="container mx-auto py-8">
        <h1 className="text-2xl font-bold mb-6 px-4 text-white">股票推荐</h1>
        <Suspense fallback={<Loading />}>
          <StockContent />
        </Suspense>
      </div>
    </div>
  );
}

function StockContent() {
  const { stocks, loading, error } = useStockData();
  
  return (
    <StockList 
      stocks={stocks} 
      loading={loading} 
      error={error} 
    />
  );
}