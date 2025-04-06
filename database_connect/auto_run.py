from apscheduler.schedulers.blocking import BlockingScheduler
from db_multithread import main as multithread_main  # 导入你上传的多线程脚本的main函数

# 定义定时任务
def job():
    print("任务开始...")
    multithread_main()  # 调用多线程脚本中的main函数
    print("任务完成！")

# 设置调度器
scheduler = BlockingScheduler()

# 设置任务每天早上9点执行
scheduler.add_job(job, 'cron', hour=8, minute=0)  # 每天9点0分执行

# 启动调度器
scheduler.start()
