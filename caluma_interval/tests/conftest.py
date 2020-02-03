import sys
from datetime import datetime

import pytest

import psycopg2
from caluma_interval.client import CalumaClient
from caluma_interval.interval import IntervalManager


@pytest.fixture
def manager():
    return IntervalManager(caluma_endpoint="http://caluma:8000/graphql")


@pytest.fixture
def client():
    return CalumaClient(endpoint="http://caluma:8000/graphql")


@pytest.fixture
def auth_client():
    return CalumaClient(
        endpoint="http://caluma:8000/graphql",
        oidc_client_id="id",
        oidc_client_secret="secret",
        oidc_token_uri="uri",
    )


@pytest.fixture()
def token():
    return {
        "access_token": "6c7dfa20995640c28e0eba82c5c88271",
        "expires_in": 300,
        "token_type": "bearer",
        "scope": ["caluma"],
        "expires_at": 1553154201.6981535,
        "expires_at_dt": datetime(2019, 3, 21, 7, 43, 21),
    }


@pytest.fixture
def create_forms(client):
    query = """\
mutation MyForm {
  firstIntSave: saveForm (input: {
    slug: "my-first-interval-form",
    name: "my first interval Form"
    meta: "{\\"interval\\": {\\"interval\\": \\"2018-03-01/P2W\\", \\"weekday\\": 1, \\"workflow_slug\\": \\"my-test-workflow\\"}}"
  }) {
    form {
      slug
    }
  }
  secondIntSave: saveForm (input: {
    slug: "my-second-interval-form",
    name: "my second interval Form"
    meta: "{\\"interval\\": {\\"interval\\": \\"2018-03-01/P2W\\", \\"weekday\\": 1, \\"workflow_slug\\": \\"my-test-workflow\\"}}"
  }) {
    form {
      slug
    }
  }
  nonIntSave: saveForm (input: {
    slug: "my-non-interval-form",
    name: "my non-interval Form"
  }) {
    form {
      slug
    }
  }
}\
"""
    return client.execute(query)


@pytest.fixture
def create_task(client):
    query = """\
mutation MySimpleTask {
  saveSimpleTask (input: {
    slug: "my-start-case-task",
    name: "my start case Task"
  }) {
    clientMutationId
  }
}\
"""
    return client.execute(query)


@pytest.fixture
def create_workflow(client):
    add_workflow = """\
mutation saveWorkFlow {
  saveWorkflow(input: {
    slug: "my-test-workflow"
    name: "my workflow"
    startTasks: ["my-start-case-task"]
    isPublished: true
    allowAllForms: true
  }) {
    clientMutationId
  }
}\
"""

    client.execute(add_workflow)


@pytest.fixture
def create_form_to_workflow(create_forms, create_task, create_workflow):
    pass


@pytest.fixture()
def cleanup_db():
    """
    Remove all rows from all touched tables in the caluma db.
    This is run after every test, to make sure we have a clean db.
    """
    yield
    conn = psycopg2.connect(
        host="db", database="caluma", user="caluma", password="caluma"
    )
    cur = conn.cursor()
    fmt_str = "DELETE FROM {};"
    tables = [
        "caluma_workflow_workitem",
        "caluma_workflow_case",
        "caluma_form_document",
        "caluma_form_form",
        "caluma_workflow_taskflow",
        "caluma_workflow_flow",
        "caluma_workflow_workflow_start_tasks",
        "caluma_workflow_workflow_allow_forms",
        "caluma_workflow_task",
        "caluma_workflow_workflow",
    ]
    for table in tables:
        delete_sql = fmt_str.format(table)
        cur.execute(delete_sql)
        conn.commit()

    cur.close()
    conn.close()


@pytest.fixture()
def sys_argv_handler():
    old_sys_argv = sys.argv
    yield
    sys.argv = old_sys_argv
