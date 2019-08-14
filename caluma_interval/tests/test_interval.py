from datetime import date, timedelta

import pytest
from isodate.duration import Duration


def test_get_intervalled_forms(manager, create_forms, cleanup_db):
    forms = manager.get_intervalled_forms()
    assert len(forms) == 2


@pytest.mark.parametrize(
    "value,exp_startdate,exp_duration",
    [
        (
            "2018-03-01/P1Y2M10D",
            Duration(10, 0, 0, years=1, months=2),
            date(2018, 3, 1),
        ),
        ("P2W", timedelta(14), None),
        ("P1Y2M1p0D", False, False),
        ("P1Y2M10DT2H30M", False, False),
        ("not a date/P2W", False, False),
        ("2018-03-01/P2W/", False, False),
    ],
)
def test_parse_interval(manager, value, exp_startdate, exp_duration):
    startdate, duration = manager.parse_interval(value)
    assert startdate == exp_startdate
    assert duration == exp_duration


def test_run_new_form(client, manager, create_form_to_workflow, cleanup_db):
    query = """\
    query allCases {
      allCases (workflow: "my-test-workflow") {
        pageInfo {
          startCursor
          endCursor
        }
        edges {
          node {
            id
          }
        }
      }
    }\
    """
    resp = client.execute(query)
    assert len(resp["data"]["allCases"]["edges"]) == 0
    manager.run()
    resp = client.execute(query)
    assert len(resp["data"]["allCases"]["edges"]) == 2


def test_run_existing_case(manager):
    data = {
        "meta": {
            "interval": {
                "weekday": "tue",
                "interval": "2018-03-01/P2W",
                "workflow_slug": "my-test-workflow",
            }
        },
        "id": "Rm9ybTpteS1pbnRlcnZhbC1mb3Jt",
        "slug": "my-interval-form",
        "documents": {
            "edges": [
                {
                    "node": {
                        "case": {
                            "closedAt": None,
                            "closedByUser": None,
                            "status": "RUNNING",
                        }
                    }
                }
            ]
        },
    }

    assert not manager.get_last_run(data)

    data = {
        "meta": {
            "interval": {
                "weekday": "tue",
                "interval": "2018-03-01/P2W",
                "workflow_slug": "my-test-workflow",
            }
        },
        "id": "Rm9ybTpteS1pbnRlcnZhbC1mb3Jt",
        "slug": "my-interval-form",
        "documents": {
            "edges": [
                {
                    "node": {
                        "case": {
                            "closedAt": "2019-03-01",
                            "closedByUser": 5,
                            "status": "COMPLETED",
                        }
                    }
                }
            ]
        },
    }

    assert manager.get_last_run(data) == date(2019, 3, 1)


def test_needs_action(manager):
    kwargs = {
        "last_run": date(2018, 1, 1),
        "interval": timedelta(14),
        "start": date(2017, 1, 1),
    }

    assert manager.needs_action(**kwargs)

    kwargs["last_run"] = date.today() - timedelta(days=13)
    assert not manager.needs_action(**kwargs)

    kwargs["weekday"] = date.today().weekday() - 2
    assert manager.needs_action(**kwargs)

    kwargs["start"] = date.today() + timedelta(days=5)
    assert not manager.needs_action(**kwargs)

    kwargs["start"] = None
    assert manager.needs_action(**kwargs)
