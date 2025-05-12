from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess
import logging
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='scheduler.log'
)

logger = logging.getLogger('scheduler')

def run_market_data_collector():
    """运行市场数据采集脚本"""
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'market_data_collector.py')
        subprocess.run(['python', script_path], check=True)
        logger.info("市场数据采集脚本执行成功")
    except subprocess.CalledProcessError as e:
        logger.error(f"市场数据采集脚本执行失败: {str(e)}")
    except Exception as e:
        logger.error(f"运行市场数据采集脚本时发生错误: {str(e)}")

def main():
    scheduler = BlockingScheduler()
    
    # 每分钟运行一次市场数据采集
    scheduler.add_job(run_market_data_collector, 'interval', minutes=1)
    
    logger.info("定时任务调度器已启动")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("定时任务调度器已停止")
    except Exception as e:
        logger.error(f"定时任务调度器发生错误: {str(e)}")

if __name__ == "__main__":
    main()