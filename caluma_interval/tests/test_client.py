import pytest
from requests.exceptions import MissingSchema
from requests_oauthlib import OAuth2Session

from caluma_interval.queries import intervalled_forms_query


def test_use_client(client):
    query = """\
query allForms {
  allForms{
    pageInfo {
      startCursor
      endCursor
    }
    edges {
      node {
        name
        meta
      }
    }
  }
}\
"""

    resp = client.execute(query)
    assert "allForms" in resp["data"]


def test_client_exception(client):
    client.endpoint = "not a uri"
    with pytest.raises(MissingSchema):
        client.execute("not a query")


def test_get_token(mocker, auth_client, token):
    mocker.patch.object(OAuth2Session, "fetch_token")
    OAuth2Session.fetch_token.return_value = token
    assert auth_client.get_token() == token


def test_authenticated_request(mocker, auth_client, token):
    mocker.patch.object(OAuth2Session, "fetch_token")
    OAuth2Session.fetch_token.return_value = token
    auth_client.execute(intervalled_forms_query)
    OAuth2Session.fetch_token.assert_called()
