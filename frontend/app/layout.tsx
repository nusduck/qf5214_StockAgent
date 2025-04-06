import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Navbar from '@/components/navbar';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'QuantAI - 智能量化分析',
  description: '基于AI的股票分析和研究报告系统',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh">
      <body className={`${inter.className} min-h-screen bg-black/[0.96] antialiased bg-grid-white/[0.02]`}>
        <div className="relative">
          <Navbar />
          <main>
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
