"use client"

import * as React from "react"
import { addMonths, format } from "date-fns"
import { Calendar as CalendarIcon, Check } from "lucide-react"
import { DateRange } from "react-day-picker"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

interface DatePickerWithRangeProps {
  date?: DateRange | undefined
  onDateChange: (date: DateRange | undefined) => void
  className?: string
}

export function DatePickerWithRange({
  date,
  onDateChange,
  className,
}: DatePickerWithRangeProps) {
  const [open, setOpen] = React.useState(false);
  
  // 分别存储左右两个月份视图的月份
  const [leftMonth, setLeftMonth] = React.useState<Date>(date?.from || new Date());
  const [rightMonth, setRightMonth] = React.useState<Date>(
    date?.to || addMonths(new Date(), 1)
  );
  
  // 当左右月份选择器的月份改变时，分别更新状态
  const handleLeftMonthChange = (month: Date) => {
    setLeftMonth(month);
  };
  
  const handleRightMonthChange = (month: Date) => {
    setRightMonth(month);
  };
  
  // 预设日期快速选择
  const selectToday = () => {
    const today = new Date();
    onDateChange({ from: today, to: today });
    setOpen(false);
  }
  
  const selectLastWeek = () => {
    const today = new Date();
    const lastWeek = new Date(today);
    lastWeek.setDate(today.getDate() - 7);
    onDateChange({ from: lastWeek, to: today });
    setOpen(false);
  }
  
  const selectLastMonth = () => {
    const today = new Date();
    const lastMonth = new Date(today);
    lastMonth.setMonth(today.getMonth() - 1);
    onDateChange({ from: lastMonth, to: today });
    setOpen(false);
  }
  
  const selectLast3Months = () => {
    const today = new Date();
    const last3Months = new Date(today);
    last3Months.setMonth(today.getMonth() - 3);
    onDateChange({ from: last3Months, to: today });
    setOpen(false);
  }
  
  // 确认日期选择
  const confirmDateSelection = () => {
    setOpen(false);
  }

  return (
    <div className={cn("grid gap-2", className)}>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            id="date"
            variant={"outline"}
            className={cn(
              "w-[280px] justify-start text-left font-normal",
              !date && "text-muted-foreground"
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {date?.from ? (
              date.to ? (
                <>
                  {format(date.from, "yyyy-MM-dd")} ~ {format(date.to, "yyyy-MM-dd")}
                </>
              ) : (
                format(date.from, "yyyy-MM-dd")
              )
            ) : (
              <span>选择日期范围</span>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <div className="p-2 border-b border-border flex flex-wrap gap-2">
            <Button size="sm" variant="outline" onClick={selectToday} className="h-8 px-2 py-0">
              今天
            </Button>
            <Button size="sm" variant="outline" onClick={selectLastWeek} className="h-8 px-2 py-0">
              近一周
            </Button>
            <Button size="sm" variant="outline" onClick={selectLastMonth} className="h-8 px-2 py-0">
              近一月
            </Button>
            <Button size="sm" variant="outline" onClick={selectLast3Months} className="h-8 px-2 py-0">
              近三月
            </Button>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4 p-3">
            {/* 左侧月份 */}
            <div className="flex-1">
              <Calendar
                mode="range"
                selected={date}
                onSelect={onDateChange}
                month={leftMonth}
                onMonthChange={handleLeftMonthChange}
                numberOfMonths={1}
                fixedWeeks
                captionLayout="dropdown-buttons"
                today={new Date()}
                disabled={[]}
                toDate={new Date()}
              />
            </div>
            
            {/* 右侧月份 */}
            <div className="flex-1">
              <Calendar
                mode="range"
                selected={date}
                onSelect={onDateChange}
                month={rightMonth}
                onMonthChange={handleRightMonthChange}
                numberOfMonths={1}
                fixedWeeks
                captionLayout="dropdown-buttons"
                today={new Date()}
                disabled={[]}
                toDate={new Date()}
              />
            </div>
          </div>
          
          <div className="p-2 border-t border-border flex justify-end">
            <Button size="sm" onClick={confirmDateSelection} className="bg-primary text-primary-foreground hover:bg-primary/90">
              <Check className="mr-2 h-4 w-4" /> 确认
            </Button>
          </div>
        </PopoverContent>
      </Popover>
    </div>
  )
} 