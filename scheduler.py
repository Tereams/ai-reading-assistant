import json
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from core.emailer import send_reading_reminder,send_summary_reminder
from core.llm_preread import llm_pre_read
from logging_config import logger

USER_FILE = "resource/user.json"

def task_morning():
    logger.info("Executing morning task: sending reading reminder and generating questions.")
    send_reading_reminder()
    llm_pre_read()

def task_everning():
    logger.info("Executing evening task: sending summary reminder.")
    send_summary_reminder()

# read scheduled time from file
def read_times_from_json():
    with open(USER_FILE, "r", encoding="utf-8") as f:
        user_data = json.load(f)

    def parse_time_string(t_str):
        parts = t_str.strip().split(":")
        hour = int(parts[0])
        minute = int(parts[1])
        return hour, minute

    morning_hm = parse_time_string(user_data["reminder_morning"])
    evening_hm = parse_time_string(user_data["reminder_evening"])
    logger.info(f"Reminder times loaded from JSON: Morning at {morning_hm[0]:02d}:{morning_hm[1]:02d}, Evening at {evening_hm[0]:02d}:{evening_hm[1]:02d}")

    return morning_hm, evening_hm

def load_and_schedule_times():
    global scheduler
    logger.info(f"[{datetime.now()}] Reloading reminder schedule...")

    # Remove previous reminder jobs
    for job in scheduler.get_jobs():
        if job.id.startswith("reminder_"):
            scheduler.remove_job(job.id)
            logger.info(f"Removed previous job: {job.id}")

    (h1, m1), (h2, m2) = read_times_from_json()

    scheduler.add_job(lambda: task_morning(),
                      CronTrigger(hour=h1, minute=m1),
                      id="reminder_morning")
    logger.info(f"Scheduled morning reminder at {h1:02d}:{m1:02d}")

    scheduler.add_job(lambda: task_everning(),
                      CronTrigger(hour=h2, minute=m2),
                      id="reminder_evening")
    logger.info(f"Scheduled evening reminder at {h2:02d}:{m2:02d}")


if __name__=='__main__':
    logger.info("Scheduler started.")
    scheduler = BlockingScheduler()
    
    # Load initial reminders
    load_and_schedule_times()

    # Reload every day at midnight
    scheduler.add_job(load_and_schedule_times, CronTrigger(hour=0, minute=0), id="daily_reload")
    logger.info("Scheduled daily config reload at 00:00.")

    scheduler.start()
