import json
import logging
from datetime import datetime, timedelta

import requests
from envparse import env
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

logger = logging.getLogger(__name__)


class CalumaClient:
    def __init__(
        self,
        endpoint=env("CALUMA_ENDPOINT", default="http://caluma:8000/graphql"),
        oidc_client_id=env("OIDC_CLIENT_ID", default=None),
        oidc_client_secret=env("OIDC_CLIENT_SECRET", default=None),
        oidc_token_uri=env("OIDC_TOKEN_URI", default=None),
    ):
        self.endpoint = endpoint
        self.oidc_client_id = oidc_client_id
        self.oidc_client_secret = oidc_client_secret
        self.oidc_token_uri = oidc_token_uri

        self._token = None

    def get_token(self):
        """
        If needed fetch a (new) token from the oidc provider.

        The threshold for fetching a new token is 1 minute before expiration.

        :return: dict
        """
        if not all([self.oidc_client_id, self.oidc_client_secret, self.oidc_token_uri]):
            logger.warning("Auth disabled due to missing parameters!")
            return

        thresh = datetime.now() + timedelta(minutes=1)

        if self._token is None or self._token["expires_at_dt"] <= thresh:
            client = BackendApplicationClient(client_id=self.oidc_client_id)
            oauth = OAuth2Session(client=client)
            self._token = oauth.fetch_token(
                token_url=self.oidc_token_uri,
                client_id=self.oidc_client_id,
                client_secret=self.oidc_client_secret,
            )
            self._token["expires_at_dt"] = datetime.utcfromtimestamp(
                int(self._token["expires_at"])
            )

        return self._token

    def execute(self, query, variables=None):
        return self._send(query, json.dumps(variables))

    def _send(self, query, variables):
        data = {"query": query, "variables": variables}
        headers = {"Accept": "application/json", "Content-Type": "application/json"}

        token = self.get_token()
        if token:
            headers["Authorization"] = f"Bearer {token['access_token']}"

        response = requests.post(self.endpoint, json=data, headers=headers)
        return response.json()
