import pytest
from requests.exceptions import MissingSchema


def test_client_exception(client):
    client.endpoint = "not a uri"
    with pytest.raises(MissingSchema):
        client.execute("not a query")
