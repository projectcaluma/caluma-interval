import sys

import pytest

import psycopg2

from .interval import IntervalManager


@pytest.fixture
def manager():
    return IntervalManager(caluma_uri="http://caluma:8000/graphql")


@pytest.fixture
def client(manager):
    return manager.client


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
        "workflow_workitem",
        "workflow_case",
        "form_document",
        "form_form",
        "workflow_taskflow",
        "workflow_flow",
        "workflow_workflow_start_tasks",
        "workflow_workflow_allow_forms",
        "workflow_task",
        "workflow_workflow",
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
