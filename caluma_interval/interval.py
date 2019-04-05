import logging
import re
from datetime import date, timedelta

from envparse import env
from isodate import isoerror, parse_date, parse_duration

from caluma_interval.client import CalumaClient
from caluma_interval.queries import intervalled_forms_query, start_case_mutation

logger = logging.getLogger(__name__)


__title__ = "caluma_interval"
__description__ = "Caluma companion app for periodic usage of forms"
__version__ = "0.0.1"
__author__ = "Adfinis SyGroup"


ISO8601_PERIOD_DATE_REGEX = re.compile(
    r"""
     ^P(?!$)
     (\d+(?:[,.]\d+)?Y)?
     (\d+(?:[,.]\d+)?M)?
     (\d+(?:[,.]\d+)?W)?
     (\d+(?:[,.]\d+)?D)?
     $
 """,
    re.VERBOSE,
)


class IntervalManager:
    def __init__(
        self,
        caluma_endpoint=env("CALUMA_ENDPOINT", default="http://caluma:8000/graphql"),
        oidc_client_id=env("OIDC_CLIENT_ID", default=None),
        oidc_client_secret=env("OIDC_CLIENT_SECRET", default=None),
        oidc_token_uri=env("OIDC_TOKEN_URI", default=None),
    ):
        self.caluma_endpoint = caluma_endpoint
        self.oidc_client_id = oidc_client_id
        self.oidc_client_secret = oidc_client_secret
        self.oidc_token_uri = oidc_token_uri

        self._client = None
        self.action_count = 0

    @property
    def client(self):
        if not self._client:
            self._client = CalumaClient(
                self.caluma_endpoint,
                self.oidc_client_id,
                self.oidc_client_secret,
                self.oidc_token_uri,
            )
        return self._client

    def get_intervalled_forms(self):
        logger.debug("Fetching intervalled forms.")
        resp = self.client.execute(intervalled_forms_query)
        return resp["data"]["allForms"]["edges"]

    def start_case(self, form):
        variables = {
            "case": {
                "form": form["slug"],
                "workflow": form["meta"]["interval"]["workflow_slug"],
            }
        }
        resp = self.client.execute(start_case_mutation, variables)
        case_id = resp["data"]["startCase"]["case"]["id"]
        logger.debug(f'Started case ID "{case_id}" for form: "{form["slug"]}".')
        self.action_count += 1

    @staticmethod
    def parse_startdate(value):
        try:
            return parse_date(value)
        except isoerror.ISO8601Error:
            return False

    @staticmethod
    def parse_duration(value):
        if not re.match(ISO8601_PERIOD_DATE_REGEX, value):
            return False
        try:
            return parse_duration(value)
        # We exclude this from coverage, because it should be prevented by our
        # own regex check
        except isoerror.ISO8601Error:  # pragma: no cover
            return False

    def parse_interval(self, interval):
        def handle_parse_error(part, value):
            logger.error(f"Couldn't parse {part} {value}")
            return False, False

        interval = interval.split("/")
        if len(interval) > 2 or len(interval) < 1:
            return handle_parse_error("interval", interval)

        start = None
        if len(interval) == 2:
            start = self.parse_startdate(interval[0])
            if start is False:
                return handle_parse_error("startdate", interval[0])

        duration = self.parse_duration(interval[-1])
        if duration is False:
            return handle_parse_error("duration", interval[-1])

        return duration, start

    @staticmethod
    def get_last_run(form):
        """
        Iterate over all cases of a form and find the date of the last successful run.
        Defaults to 1900-01-01 if never run
        Returns False if a case is already running
        """
        last_run = date(1900, 1, 1)
        for document in form["documents"]["edges"]:
            case = document["node"]["case"]
            if case["status"] == "RUNNING":
                return False
            elif case["status"] == "COMPLETED":
                closed_at = parse_date(case["closedAt"])
                if closed_at > last_run:
                    last_run = closed_at
        logger.debug(f'Form: {form["slug"]} was last run on {last_run}.')
        return last_run

    @staticmethod
    def get_last_weekday(dt, weekday):
        """
        Based on a provided date, find last date on a specified weekday.
        :param dt: date
        :param weekday: int
        :return: date
        """
        gap = weekday - dt.weekday()
        if gap >= 0:
            gap -= 7
        return dt + timedelta(days=gap)

    def needs_action(self, last_run, interval, start, weekday=None):
        now = date.today()
        if start > now:
            return False
        next_run = last_run + interval
        if weekday is not None:
            if not next_run.weekday() == weekday:
                next_run = self.get_last_weekday(next_run, weekday)
        if next_run < now:
            return True

    def handle_form(self, form):
        last_run = self.get_last_run(form)
        if last_run is False:
            return
        interval, start = self.parse_interval(form["meta"]["interval"]["interval"])
        if interval is False:
            return
        weekday = form["meta"]["interval"].get("weekday")

        if self.needs_action(last_run, interval, start, weekday):
            self.start_case(form)

    def run(self):
        forms = self.get_intervalled_forms()
        logger.info(f"Got {len(forms)} intervalled forms from caluma.")
        for form in forms:
            self.handle_form(form["node"])
        logger.info(f"Started {self.action_count} case(s).")
