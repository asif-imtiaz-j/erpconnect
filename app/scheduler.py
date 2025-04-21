from apscheduler.schedulers.background import BackgroundScheduler
from app.utils import print_reminder_emails
import logging

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(print_reminder_emails, 'interval', days=1)
    
    try:
        scheduler.start()
        logging.info("✅ Scheduler started for invoice reminders.")
    except Exception as e:
        logging.error(f"❌ Failed to start scheduler: {e}")
