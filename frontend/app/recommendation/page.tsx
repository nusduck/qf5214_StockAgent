'use client';

import { Suspense } from 'react';
import Loading from './loading';

export default function RecommendationPage() {
  return (
    <Suspense fallback={<Loading />}>
      <div>
        {/* 你的推荐页面内容 */}
      </div>
    </Suspense>
  );
}