import pytest

from lambda_functions.v1.functions.lpa_codes.app.api import code_generator


@pytest.fixture()
def broken_get_code(monkeypatch):
    def mock_get_codes():
        print("broken method - mock_get_code")
        raise Exception

    monkeypatch.setattr(code_generator, "get_codes", mock_get_codes)


@pytest.fixture()
def broken_generate_code(monkeypatch):
    def mock_generate_code():
        print("broken method - mock_generate_code")
        raise Exception

    monkeypatch.setattr(code_generator, "generate_code", mock_generate_code)


@pytest.fixture()
def broken_insert_new_code(monkeypatch):
    def mock_insert_new_code():
        print("broken method - mock_insert_new_code")
        raise Exception

    monkeypatch.setattr(code_generator, "insert_new_code", mock_insert_new_code)


@pytest.fixture()
def broken_update_codes(monkeypatch):
    def mock_update_codes():
        print("broken method - mock_update_codes")
        raise Exception

    monkeypatch.setattr(code_generator, "update_codes", mock_update_codes)
