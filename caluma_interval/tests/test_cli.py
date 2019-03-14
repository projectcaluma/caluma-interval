import sys

from caluma_interval.__main__ import main, parse_arguments


def test_arg_parsing():
    args = parse_arguments(["-c", "http://caluma:8000/graphql", "-d"])

    assert args.caluma_uri == "http://caluma:8000/graphql"
    assert args.debug

    args = parse_arguments([])
    assert not args.debug


def test_main(sys_argv_handler, create_form_to_workflow, cleanup_db):
    sys.argv = ["__main__.py", "-c", "http://caluma:8000/graphql", "-d"]
    main()

    sys.argv = ["__main__.py", "-c", "http://caluma:8000/graphql"]
    main()
