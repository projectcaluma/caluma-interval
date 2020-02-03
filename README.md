# caluma-interval

[![Build Status](https://travis-ci.com/projectcaluma/caluma-interval.svg?branch=master)](https://travis-ci.org/projectcaluma/caluma-interval)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/projectcaluma/caluma-interval/blob/master/.coveragerc#L5)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/projectcaluma/caluma-interval)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

[Caluma](https://caluma.io/) companion app for periodic usage of forms.


## Periodic usage of forms

There are forms you might want to use periodically. This project adds support for this
by utilizing the `meta`-field of forms.

## Example use case

Your flux capacitor needs new plutonium once every two weeks. So you have a form
`refill-plutonium-in-flux-capacitor` you want to use every two weeks.

This can be achieved with following interval inside the meta field of this form:

```json
{
    "interval": {
        "interval": "P2W",
        "workflow_slug": "delorean-workflow"
    }
}
```

This will make sure, that exactly two weeks after the last refill, a new case will be
opened for this form.

Now let's say, it's important to you, that this case is always opened on a monday
(shortening the interval if needed). Further you want to set a start date, to make sure
no case will be opened before that.

This can be achieved with following interval:

```json
{
    "interval": {
        "interval": "2019-03-18/P2W",
        "weekday": 0,
        "workflow_slug": "delorean-workflow"
    }
}
```

## Features

 * Handle periodic usage of forms
 * Optionally set a start date
 * Optionally force a specific weekday
 * Will never start multiple cases for the same form


## Meta field

The `meta`-field is a JSONField and can be found on a variety of Caluma-objects. We're
only interested in forms though.

## Interval definition

caluma-interval checks the `meta`-field of forms for an `interval`-key.

Example:

```json
{
    "interval": {
        "interval": "2018-03-01/P1Y2M10D",
        "weekday": 1,
        "workflow_slug": "my-test-workflow"
    }
}
```

### Fields

#### interval

[ISO8601 time interval notation](https://en.wikipedia.org/wiki/ISO_8601#Time_intervals).

We use `{{startdate}}/{{duration}}`, where **startdate** is optional. If omitted, the
case will be opened immediately.

For duration we use a subset of
[ISO8601 duration](https://en.wikipedia.org/wiki/ISO_8601#Durations) without time.

You can find the regex we use below in [ValidationClass](#validationclass).

#### weekday

An optional weekday (zero-indexed integer). This makes sure, that only on this weekday
a case for this form will be started.

This will never exceed the configured interval.


#### workflow_slug

The slug for the corresponding workflow.


## Configuration
You can configure caluma_interval with environment variables or CLI arguments, whereas
CLI arguments take precedence.

```
usage: __main__.py [-h] [-c STRING] [-i STRING] [-s STRING] [-u STRING] [-d]
                   [-v]

Caluma companion app for periodic usage of forms

optional arguments:
  -h, --help            show this help message and exit
  -c STRING, --caluma-endpoint STRING
                        defaults to "http://caluma:8000/graphql"
  -i STRING, --oidc-client-id STRING
  -s STRING, --oidc-client-secret STRING
  -u STRING, --oidc-token-uri STRING
  -d, --debug           print debug messages
  -v, --version         show program's version number and exit
```

The corresponding environment variables are:
 * CALUMA_ENDPOINT - defaults to `http://caluma:8000/graphql`
 * OIDC_CLIENT_ID
 * OIDC_CLIENT_SECRET
 * OIDC_TOKEN_URI

Additional environment variables for when using the docker image:
 * CALUMA_HOST - defaults to `caluma`
 * CALUMA_PORT - defaults to `8000`

To enable oidc authentication over plain http (only for testing!), set
`OAUTHLIB_INSECURE_TRANSPORT` to `1`.


## Authentication
As Caluma uses OpenID Connect (OIDC), we need to fetch a token from the OIDC provider.

For this you have to provide a client id, client secret and a token uri.

If none of them are provided, the client will make unauthenticated requests, which
(hopefully) will fail in your prod setup.

## ValidationClass

You may want to add a custom ValidationClass to Caluma in order to validate the content
of `meta['interval']`:

```python
import re
from datetime import datetime

from caluma.core.validations import BaseValidation, validation_for
from caluma.form.schema import SaveForm
from caluma.workflow.models import Workflow
from rest_framework import exceptions


# Regex to parse ISO8601 periods WITHOUT time information
ISO8601_PERIOD_DATE_REGEX = re.compile(
    r"^P(?!$)"
    r"(\d+(?:[,\.]\d+)?Y)?"
    r"(\d+(?:[,\.]\d+)?M)?"
    r"(\d+(?:[,\.]\d+)?W)?"
    r"(\d+(?:[,\.]\d+)?D)?$"
)


def validate_interval(interval):
    interval_list = interval["interval"].split("/")
    if len(interval_list) == 2:
        try:
            datetime.strptime(interval_list[0], "%Y-%m-%d")
        except ValueError:
            raise exceptions.ValidationException("Failed to parse startdate!")
    elif len(interval_list) > 2:
        raise exceptions.ValidationException("Failed to parse interval!")

    if not ISO8601_PERIOD_DATE_REGEX.match(interval_list[-1]):
        raise exceptions.ValidationException("Failed to parse period!")


class FormIntervalValidation(BaseValidation):
    @validation_for(SaveForm)
    def validate_save_form(self, mutation, data, info):
        if "meta" not in data and "interval" not in data["meta"]:
            return data
        interval = data["meta"]["interval"]

        if "interval" not in interval:
            raise exceptions.ValidationException("Interval must be set!")

        if "workflow_slug" not in interval:
            raise exceptions.ValidationException("workflow_slug must be set!")

        try:
            Workflow.obj.get(slug=interval["workflow_slug"])
        except Workflow.DoesNotExist:
            raise exceptions.ValidationException(
                "Failed to get workflow with provided workflow_slug!"
            )

        if "weekday" in interval:
            if not interval["weekday"] >= 0 <= 6:
                raise exceptions.ValidationException(
                    "Weekday must be an integer from 0 to 6!"
                )

        validate_interval(interval['interval'])
```

## docker-compose integration

```
interval:
  image: projectcaluma/caluma-interval:latest
  build:
    context: .
  depends_on:
    - caluma
```

## Contribution
We use following tools in order to standardize development and releases:

 * flake8
 * black
 * isort
 * commitlint

### pre-commit hooks

Pre commit hooks is an additional option instead of executing checks in your editor of choice.

First create a virtualenv with the tool of your choice before running below commands:

```bash
pip install pre-commit
pip install -r requirements-dev.txt -U
pre-commit install
pre-commit install --hook=pre-commit
pre-commit install --hook=commit-msg
```
