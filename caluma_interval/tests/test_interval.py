from datetime import date, timedelta

from isodate.duration import Duration


def test_get_intervalled_forms(manager, create_forms, cleanup_db):
    forms = manager.get_intervalled_forms()
    assert len(forms) == 2


def test_parse_interval(manager):
    test_strings = [
        {
            "value": "2018-03-01/P1Y2M10D",
            "expected": [Duration(10, 0, 0, years=1, months=2), date(2018, 3, 1)],
        },
        {"value": "P2W", "expected": [timedelta(14), None]},
    ]

    for test in test_strings:
        result = manager.parse_interval(test["value"])
        assert result[0] == test["expected"][0]
        assert result[1] == test["expected"][1]


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
