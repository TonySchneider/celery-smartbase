# Celery SmartBase

`celery-smartbase` is an extension and improvement of the popular `celery` PyPI package. It provides features to avoid duplicates for tasks that are pending or running and to see the "pending" tasks as well in the "jobs" Django model when you integrate Celery with Django. Although this package is improved to work with Django, users can modify the features slightly to make it work with any Python framework, not just Django.

## Features

1. **Avoid Duplicate Tasks**: Prevents the creation of duplicate tasks that are either pending or running.
2. **View Pending Tasks**: Allows you to see the "pending" tasks in the "jobs" Django model when you integrate Celery with Django.

These features are developed inside an extension of the `BaseTask` class of the existing Celery Python package. The extension class is called `SmartBase`.

## SmartBase Class

The `SmartBase` class is an extension of the `BaseTask` class from the Celery package. Here is the code for the `SmartBase` class:

```python
class SmartBase(BaseTask):
...
```

[Include the full code of the SmartBase class here]

## Requirements

- Django
- djangorestframework
- django-model-utils
- django-celery-results
- django-celery-beat
- kombu
- celery

## Installation

To install the `celery-smartbase` package, run the following command:

```
pip install celery-smartbase
```

## Usage

To use the `celery-smartbase` package, you need to...

[Include examples of how to use the package here]

## Contributing

If you would like to contribute to the `celery-smartbase` package, please...

[Include information on how others can contribute to your package]

## License

The `celery-smartbase` package is licensed under the...

[Include information about the license of your package]

## Acknowledgments

[Include any acknowledgments or credits you would like to include]
