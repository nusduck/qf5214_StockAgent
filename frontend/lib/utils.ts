import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatNumber(num: number | null | undefined): string {
  if (num === null || num === undefined) return '--';
  return num.toLocaleString('zh-CN');
}

export function formatPercent(num: number | null | undefined): string {
  if (num === null || num === undefined) return '--';
  const value = Number(num);
  if (isNaN(value)) return '--';
  return (value >= 0 ? '+' : '') + value.toFixed(2) + '%';
}

export function formatDate(date: Date): string {
  return date.toISOString().slice(0, 10).replace(/-/g, '');
}
