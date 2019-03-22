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


def test_main_failure(sys_argv_handler, create_form_to_workflow, cleanup_db, caplog):
    sys.argv = ["__main__.py", "-c", "http://nothing-here", "-d"]
    main()
    assert caplog.records[-1].levelname == "ERROR"
