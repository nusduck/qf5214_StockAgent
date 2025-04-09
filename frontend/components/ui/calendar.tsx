"use client"

import * as React from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { DayPicker, useNavigation } from "react-day-picker"
import { format, getYear, getMonth, setMonth, setYear } from "date-fns"
import { zhCN } from "date-fns/locale"

import { cn } from "@/lib/utils"
import { buttonVariants } from "@/components/ui/button"
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select"

export type CalendarProps = React.ComponentProps<typeof DayPicker>

// 自定义导航条组件，添加年月选择
function CustomCaption({ displayMonth, onMonthChange, ...props }: any) {
  const { goToMonth, nextMonth, previousMonth } = useNavigation();
  
  // 检查是否是第二个月的标题 (右侧)
  const isSecondMonth = props?.id?.includes('1');
  
  // 生成年份选项（从2015年到当前年份）
  const todayYear = new Date().getFullYear(); // 获取当前实际年份
  const years = Array.from({ length: 11 }, (_, i) => todayYear - 10 + i);
  
  // 生成月份选项
  const months = [
    { value: 0, label: "1月" },
    { value: 1, label: "2月" },
    { value: 2, label: "3月" },
    { value: 3, label: "4月" },
    { value: 4, label: "5月" },
    { value: 5, label: "6月" },
    { value: 6, label: "7月" },
    { value: 7, label: "8月" },
    { value: 8, label: "9月" },
    { value: 9, label: "10月" },
    { value: 10, label: "11月" },
    { value: 11, label: "12月" },
  ];

  const handleYearChange = (newYear: string) => {
    const date = new Date(displayMonth);
    date.setFullYear(parseInt(newYear));
    goToMonth(date);
  };

  const handleMonthChange = (newMonth: string) => {
    const date = new Date(displayMonth);
    date.setMonth(parseInt(newMonth));
    goToMonth(date);
  };
  
  // 获取当前显示月份和年份 
  const currentMonth = getMonth(displayMonth);
  const currentYear = getYear(displayMonth);

  return (
    <div className="flex justify-center pt-1 relative items-center">
      <div className="flex items-center space-x-2">
        <button
          onClick={() => previousMonth && goToMonth(previousMonth)}
          disabled={!previousMonth}
          className={cn(
            buttonVariants({ variant: "outline" }),
            "h-7 w-7 bg-transparent p-0 opacity-50 hover:opacity-100"
          )}
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        
        <div className="flex items-center space-x-1">
          <Select
            value={String(currentYear)}
            onValueChange={handleYearChange}
          >
            <SelectTrigger className="h-7 w-[80px]">
              <SelectValue>{currentYear}</SelectValue>
            </SelectTrigger>
            <SelectContent>
              {years.map((year) => (
                <SelectItem key={year} value={String(year)}>
                  {year}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <Select
            value={String(currentMonth)}
            onValueChange={handleMonthChange}
          >
            <SelectTrigger className="h-7 w-[70px]">
              <SelectValue>{months[currentMonth].label}</SelectValue>
            </SelectTrigger>
            <SelectContent>
              {months.map((month) => (
                <SelectItem key={month.value} value={String(month.value)}>
                  {month.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        <button
          onClick={() => nextMonth && goToMonth(nextMonth)}
          disabled={!nextMonth}
          className={cn(
            buttonVariants({ variant: "outline" }),
            "h-7 w-7 bg-transparent p-0 opacity-50 hover:opacity-100"
          )}
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

function Calendar({
  className,
  classNames,
  showOutsideDays = true,
  ...props
}: CalendarProps) {
  return (
    <DayPicker
      showOutsideDays={showOutsideDays}
      className={cn("p-3", className)}
      classNames={{
        months: "flex flex-col sm:flex-row space-y-4 sm:space-x-4 sm:space-y-0",
        month: "space-y-4",
        caption: "flex justify-center pt-1 relative items-center",
        caption_label: "hidden", // 隐藏默认的标签
        nav: "space-x-1 flex items-center",
        nav_button: cn(
          buttonVariants({ variant: "outline" }),
          "h-7 w-7 bg-transparent p-0 opacity-50 hover:opacity-100"
        ),
        nav_button_previous: "hidden", // 隐藏默认的导航按钮
        nav_button_next: "hidden", // 隐藏默认的导航按钮
        table: "w-full border-collapse space-y-1",
        head_row: "flex",
        head_cell:
          "text-muted-foreground rounded-md w-9 font-normal text-[0.8rem]",
        row: "flex w-full mt-2",
        cell: "h-9 w-9 text-center text-sm p-0 relative [&:has([aria-selected].day-range-end)]:rounded-r-md [&:has([aria-selected].day-outside)]:bg-accent/50 [&:has([aria-selected])]:bg-accent first:[&:has([aria-selected])]:rounded-l-md last:[&:has([aria-selected])]:rounded-r-md focus-within:relative focus-within:z-20",
        day: cn(
          buttonVariants({ variant: "ghost" }),
          "h-9 w-9 p-0 font-normal aria-selected:opacity-100"
        ),
        day_range_end: "day-range-end",
        day_selected:
          "bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground focus:bg-primary focus:text-primary-foreground",
        day_today: "bg-accent text-accent-foreground",
        day_outside:
          "day-outside text-muted-foreground aria-selected:bg-accent/50 aria-selected:text-muted-foreground aria-selected:text-muted-foreground",
        day_disabled: "text-muted-foreground opacity-50",
        day_range_middle:
          "aria-selected:bg-accent aria-selected:text-accent-foreground",
        day_hidden: "invisible",
        ...classNames,
      }}
      components={{
        IconLeft: ({ ...props }) => <ChevronLeft className="h-4 w-4" />,
        IconRight: ({ ...props }) => <ChevronRight className="h-4 w-4" />,
        Caption: CustomCaption
      }}
      locale={zhCN}
      modifiersClassNames={{
        selected: "selected",
        disabled: "disabled"
      }}
      {...props}
    />
  )
}
Calendar.displayName = "Calendar"

export { Calendar }
