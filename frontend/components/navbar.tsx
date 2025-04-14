"use client"

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Bot, Github } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { STOCK_CONFIG } from '@/lib/constants'

export default function Navbar() {
  const pathname = usePathname()
  const [stockCode, setStockCode] = useState(STOCK_CONFIG.DEFAULT_CODE)

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    // 处理搜索逻辑
    window.location.href = `/stockanalysis?code=${stockCode}`
  }

  return (
    <nav className="border-b border-white/10 bg-black/50 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center space-x-2">
            <Bot className="w-8 h-8 text-purple-500" />
            <span className="text-white font-medium text-xl">QuantAI</span>
          </Link>

          <div className="flex items-center space-x-6">
            <Link 
              href="/" 
              className={`text-gray-300 hover:text-white ${
                pathname === '/' ? 'text-white' : ''
              }`}
            >
              Home
            </Link>
            <Link 
              href="/recommendation" 
              className={`text-gray-300 hover:text-white ${
                pathname === '/recommendation' ? 'text-white' : ''
              }`}
            >
              Recommendation
            </Link>
            <Link 
              href="/stockanalysis" 
              className={`text-gray-300 hover:text-white ${
                pathname === '/stockanalysis' ? 'text-white' : ''
              }`}
            >
              Stock Analysis
            </Link>
          </div>

          <div className="flex items-center space-x-4">
            <a 
              href="https://github.com/nusduck/qf5214_StockAgent" 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex items-center space-x-2 text-white hover:text-purple-400"
            >
              <Github className="w-6 h-6" />
              <span className="hidden sm:inline">GitHub</span>
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
}
