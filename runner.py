from app import app
from apscheduler.schedulers.background import BackgroundScheduler
from views import RemoveLogs


if __name__ == '__main__':
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(RemoveLogs, 'interval', minutes=1)
    # scheduler.start()
    app.run(host="0.0.0.0", port=80)