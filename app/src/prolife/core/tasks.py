
from celery.utils.log import get_task_logger

from prolife.celery import app

logger = get_task_logger(__name__)


# Sample Task - You can remove it. This is just for an example.

@app.task
def add(x, y):
    return x + y


