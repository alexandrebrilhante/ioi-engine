from unittest.mock import patch

import pytest

from ioi.ioi import IndicationOfInterest


@pytest.fixture
def mock_socket():
    with patch("ioi.ioi.socket.socket") as mock:
        yield mock


@pytest.fixture
def mock_env():
    with patch.dict("os.environ", {"HOST": "localhost", "PORT": "1234"}):
        yield


@pytest.fixture
def valid_tags():
    return {"symbol": "AAPL", "side": "1", "ioi_qty": "100"}


def test_initialization(valid_tags):
    with patch("ioi.ioi.simplefix.FixMessage") as mock_fix_message:
        _ioi = IndicationOfInterest(**valid_tags)

        mock_fix_message.assert_called()

        assert mock_fix_message.return_value.append_pair.call_count >= 5


def test_submit_valid(mock_socket, mock_env, valid_tags):
    ioi = IndicationOfInterest(**valid_tags)
    ioi.submit()

    mock_socket.return_value.connect.assert_called_once_with(("localhost", 1234))
    mock_socket.return_value.sendall.assert_called()


def test_submit_missing_required_fields(mock_socket, mock_env):
    with pytest.raises(AssertionError):
        ioi = IndicationOfInterest(symbol="AAPL")
        ioi.submit()


def test_replace_valid(mock_socket, mock_env):
    tags_with_ref_id = {
        "ioi_ref_id": "123",
        "symbol": "AAPL",
        "side": "1",
        "ioi_qty": "100",
    }

    ioi = IndicationOfInterest(**tags_with_ref_id)
    ioi.replace()

    mock_socket.return_value.connect.assert_called_once_with(("localhost", 1234))
    mock_socket.return_value.sendall.assert_called()


def test_replace_missing_ioi_ref_id(mock_socket, mock_env, valid_tags):
    with pytest.raises(AssertionError):
        ioi = IndicationOfInterest(**valid_tags)
        ioi.replace()


def test_cancel_valid(mock_socket, mock_env):
    tags_with_ref_id = {
        "ioi_ref_id": "123",
        "symbol": "AAPL",
        "side": "1",
        "ioi_qty": "100",
    }

    ioi = IndicationOfInterest(**tags_with_ref_id)
    ioi.cancel()

    mock_socket.return_value.connect.assert_called_once_with(("localhost", 1234))
    mock_socket.return_value.sendall.assert_called()


def test_cancel_missing_ioi_ref_id(mock_socket, mock_env, valid_tags):
    with pytest.raises(AssertionError):
        ioi = IndicationOfInterest(**valid_tags)
        ioi.cancel()
