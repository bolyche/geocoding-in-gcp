import mock
import pytest
import json

from geocode.geocoder import GeocodeIPs

FAKE_TOKEN = "123abc"
IP = "0.0.0.0"
IP_PARAM = {"ip": IP}
GEO_DATA = {"message": "useful geo data?"}
EXPECTED_GEO_RETURN = json.dumps(GEO_DATA).encode("utf-8")
# Saved broken IP data has a particular format of saving the record; worth rethinking
COMBINED = {"ip": IP, "message": GEO_DATA}

# Note that for the secrets it'd be better to mock out the connection, but since we're returning a static token here just mock out the method itself


@pytest.fixture
def mock_secret():
    with mock.patch.object(
        GeocodeIPs, "_get_api_token", return_value=FAKE_TOKEN
    ) as secret:
        yield secret


@mock.patch("requests.Session")
def test_init(mock_session, mock_secret):
    "Check init creates session with the api token and expected headers"
    geo = GeocodeIPs()

    assert mock_session.called
    assert mock_secret.called
    assert geo._request_session.params.get("apiKey") == FAKE_TOKEN
    assert geo._request_session.headers == {
        "Content-Type": "application/json",
    }


@pytest.mark.parametrize(
    "data, params",
    [(None, None), ({"a": 1}, None), ({"ip": "1.1.1.1"}, {"data": ["foobar"]})],
)
@mock.patch("requests.Session", autospec=True)
def test_get_request_call_args(mock_session, data, params, mock_secret):
    "Check session get request calls with expected args/kwargs"
    mock_session.return_value.get.return_value.status_code = 200

    geo = GeocodeIPs()
    geo._get_request(data=data, params=params)

    assert mock_session.called
    assert mock_session.return_value.get.called
    assert mock_session.return_value.get.call_args == mock.call(
        url=GeocodeIPs.GEO_URL, data=data, params=params
    )


@pytest.mark.parametrize("status_code", [401, 403, 404, 405, 413, 415, 423, 429, 499])
@mock.patch("requests.Session", autospec=True)
@mock.patch.object(GeocodeIPs, "_handle_broken_ip")
def test_get_request_bad_status_code(
    mock_handle_broken_ip, mock_session, status_code, mock_secret
):
    "Check _handle_broken_ip method called upon request having client error status code"
    mock_session.return_value.get.return_value.status_code = status_code

    geo = GeocodeIPs()
    geo._get_request(params=IP_PARAM)

    assert mock_handle_broken_ip.called
    assert mock_handle_broken_ip.call_args == mock.call(
        params=IP_PARAM, message=mock_session.return_value.get.return_value.text
    )


@mock.patch("requests.Session.get")
def test_get_ip_geo_unfiltered_returns_json(mock_get, mock_secret):
    "Check get_ip_geo_unfiltered gets expected json output via response content"
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = EXPECTED_GEO_RETURN

    geo = GeocodeIPs()
    output = geo.get_ip_geo_unfiltered(IP)

    assert output == GEO_DATA


@mock.patch("json.dump")
@mock.patch("builtins.open")
def test_handle_broken_ip(mock_open, mock_json_dump, mock_secret):
    "Check _handle_broken_ip opens a file and dumps content in the expected format"
    geo = GeocodeIPs()

    geo._handle_broken_ip(params=IP_PARAM, message=GEO_DATA)

    assert mock_open.called
    assert mock_json_dump.call_args[0][0] == COMBINED
