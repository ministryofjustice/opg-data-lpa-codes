import logging


from lambda_functions.v1.functions.lpa_codes.app.api.database import (
    db_connection,
    lpa_codes_table,
)


def test_db_connection(monkeypatch, caplog):

    monkeypatch.setenv("ENVIRONMENT", None)

    db_connection()

    with caplog.at_level(logging.INFO):
        assert "Connecting to local Docker database container" not in caplog.text

    monkeypatch.setenv("ENVIRONMENT", "mock")

    db_connection()

    with caplog.at_level(logging.INFO):
        assert "Connecting to local Docker database container" not in caplog.text

    monkeypatch.setenv("ENVIRONMENT", "local")

    db_connection()

    with caplog.at_level(logging.INFO):
        assert "Connecting to local Docker database container" in caplog.text

    monkeypatch.setenv("ENVIRONMENT", "ci")

    db_connection()

    with caplog.at_level(logging.INFO):
        assert "Connecting to local Docker database container" in caplog.text


def test_lpa_codes_table(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "mock")

    assert lpa_codes_table() == "lpa_codes"

    monkeypatch.setenv("ENVIRONMENT", "pretend_env")

    assert lpa_codes_table() == "lpa-codes-pretend_env"
