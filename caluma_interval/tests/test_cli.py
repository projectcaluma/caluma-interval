import sys

from caluma_interval.__main__ import main, parse_arguments


def test_arg_parsing():
    args = parse_arguments(["-c", "http://something", "-d"])

    assert args.caluma_endpoint == "http://something"
    assert args.debug

    args = parse_arguments([])
    assert not args.debug


def test_main(sys_argv_handler, create_form_to_workflow, cleanup_db):
    sys.argv = ["__main__.py", "-d"]
    main()

    sys.argv = ["__main__.py"]
    main()


def test_main_faulty_interval(
    client, sys_argv_handler, create_form_to_workflow, cleanup_db
):
    """
    Test handling of faulty intervals.

    We just want to know if this runs through without throwing any exception.

    This should never be needed, as Calumas ValidationClass should already
    enforce this.

    Nonetheless, here's the test:
    """
    query = """\
        mutation MyForm {
          firstIntSave: saveForm (input: {
            slug: "my-first-interval-form",
            name: "my first interval Form"
            meta: "{\\"interval\\": {\\"interval\\": \\"2018-03-01/P2Wpqli\\", \\"workflow_slug\\": \\"my-test-workflow\\"}}"
          }) {
            form {
              slug
            }
          }
        }\
    """
    client.execute(query)
    sys.argv = ["__main__.py", "-d"]
    main()


def test_main_failure(sys_argv_handler, create_form_to_workflow, cleanup_db, caplog):
    sys.argv = ["__main__.py", "-c", "http://nothing-here", "-d"]
    main()
    assert caplog.records[-1].levelname == "ERROR"
