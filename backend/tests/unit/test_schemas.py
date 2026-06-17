import pytest
from pydantic import ValidationError

from app.schemas.auth import UserRegister, UserLogin
from app.schemas.market import WatchlistAdd, SUPPORTED_SYMBOLS


class TestUserRegisterSchema:
    def _valid(self, **overrides):
        return dict(
            email="user@example.com",
            username="trader99",
            password="SecurePass1",
            **overrides,
        )

    def test_valid_data(self):
        u = UserRegister(**self._valid())
        assert u.email == "user@example.com"
        assert u.username == "trader99"

    def test_username_lowercased(self):
        u = UserRegister(**self._valid(username="TraderBOB"))
        assert u.username == "traderbob"

    def test_username_too_short(self):
        with pytest.raises(ValidationError, match="3"):
            UserRegister(**self._valid(username="ab"))

    def test_username_invalid_chars(self):
        with pytest.raises(ValidationError):
            UserRegister(**self._valid(username="trader-99!"))

    def test_password_too_short(self):
        with pytest.raises(ValidationError):
            UserRegister(**self._valid(password="Sh0rt"))

    def test_password_no_uppercase(self):
        with pytest.raises(ValidationError):
            UserRegister(**self._valid(password="alllower1"))

    def test_password_no_digit(self):
        with pytest.raises(ValidationError):
            UserRegister(**self._valid(password="NoDigitsHere"))

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            UserRegister(**self._valid(email="not-an-email"))


class TestWatchlistAddSchema:
    def test_valid_btc(self):
        w = WatchlistAdd(symbol="BTCUSDT")
        assert w.symbol == "BTCUSDT"

    def test_lowercased_input_normalised(self):
        w = WatchlistAdd(symbol="ethusdt")
        assert w.symbol == "ETHUSDT"

    def test_whitespace_stripped(self):
        w = WatchlistAdd(symbol="  SOLUSDT  ")
        assert w.symbol == "SOLUSDT"

    def test_unsupported_symbol_rejected(self):
        with pytest.raises(ValidationError):
            WatchlistAdd(symbol="FAKECOIN")

    def test_all_supported_symbols_accepted(self):
        for sym in SUPPORTED_SYMBOLS:
            w = WatchlistAdd(symbol=sym)
            assert w.symbol == sym
