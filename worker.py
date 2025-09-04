from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from ingest_x import run as run_x
from ingest_reddit import run as run_reddit
from ingest_instagram_pull import run as run_ig

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=10)
def job_x():
    print("[X] poll", datetime.now())
    run_x()

@sched.scheduled_job('interval', minutes=15)
def job_reddit():
    print("[Reddit] poll", datetime.now())
    run_reddit()

@sched.scheduled_job('interval', minutes=20)
def job_ig():
    print("[Instagram Pull] poll", datetime.now())
    run_ig()

if __name__ == "__main__":
    print("Scheduler starting…")
    sched.start()
