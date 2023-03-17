Celery Smartbase
=================

Celery Smartbase is a Python package that provides solutions for common problems that arise when working with the Celery distributed task queue. In particular, Celery Smartbase solves the problem of duplicate task execution, which can occur in certain scenarios such as when workers are restarted.

Celery Smartbase achieves this by providing a custom task class that overrides the default Celery task class. This custom task class includes a unique task ID generator that ensures that each task is executed only once, even if it is queued multiple times.

In addition to solving the duplicate task problem, Celery Smartbase also provides a set of base classes that can be overridden to add custom code and improve the performance of Celery. These base classes include:

- Task: The base class for all Celery tasks.
- TaskSet: A task set is a group of tasks that are executed together.
- Canvas: A canvas is a group of tasks that are executed sequentially or in parallel.
- Group: A group is a set of tasks that are executed in parallel.

Celery Smartbase is designed to be used with Django and requires it as a dependency. To install Celery Smartbase, simply run `pip install celery-smartbase`. Once installed, you can use the custom task class provided by Celery Smartbase by importing it in your Celery configuration file:

```python
from celery import Celery
from celery_smartbase import SmartTask

app = Celery('tasks', broker='pyamqp://guest@localhost//')
app.task_cls = SmartTask
```

Contributing
--------
Contributions to Celery Smartbase are welcome! If you find a bug or have an idea for a new feature, please open an issue or submit a pull request.

License
--------
Celery Smartbase is licensed under the MIT License. See the LICENSE file for more information.
