from celery.schedules import crontab
from gitconsensusservice.jobs import consensus
from gitconsensusservice import celery


@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        5 * 60.0,
        consensus.process_installs.s(),
        name='Root Task - Schedule Installation Jobs')
