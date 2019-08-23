from celery.schedules import crontab
from gitconsensusservice.jobs import consensus
from gitconsensusservice import celery, app


@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    print('Root Task - Schedule Installation Jobs')
    sender.add_periodic_task(
        float(app.config.get('PROCESS_INSTALLS_INTERVAL', 5 * 60.0)),
        consensus.process_installs.s(),
        name='Root Task - Schedule Installation Jobs')
