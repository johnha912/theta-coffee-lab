"""Storage, currency, stock alerts, and the email report.

Run from the repo root: python -m pytest tests  (or: python tests/test_backend.py)
Set DATABASE_URL to a PostgreSQL URL to run the same checks against Postgres.
"""
import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DATABASE_URL", f"sqlite:///{tempfile.mkdtemp()}/test.db")
import report  # noqa: E402
import store  # noqa: E402
import utils  # noqa: E402


def test_transaction_rolls_back_every_table():
    store.reset()
    try:
        with store.transaction() as save:
            save("sales", store.load("sales").head(1))
            save("inventory", store.load("inventory").head(1))
            raise RuntimeError("fails after both writes")
    except RuntimeError:
        pass
    assert len(store.load("sales")) == 205 and len(store.load("inventory")) == 20


def test_export_import_round_trip_and_validation():
    store.reset()
    frames = store.read_upload("backup.zip", store.export_zip())
    assert {t: len(df) for t, df in frames.items()} == {t: len(store.load(t)) for t in store.SCHEMA}
    store.import_frames({"products": frames["products"].head(3)})
    assert len(store.load("products")) == 3
    try:
        store.import_frames({"sales": frames["sales"].drop(columns=["Promo"]), "products": frames["products"]})
        raise AssertionError("an import with a missing column must be rejected")
    except ValueError as e:
        assert "Promo" in str(e)
    assert len(store.load("products")) == 3  # rejected import changed nothing
    store.reset()
    assert len(store.load("products")) == 17


def test_currency_follows_settings():
    st.session_state.currency = "VND"
    assert utils.format_currency(5151447) == "5,151,447 VND"
    st.session_state.currency, st.session_state.usd_rate = "USD", 26000.0
    assert utils.format_currency(52000) == "2.00 USD"
    assert utils.format_currency(float("nan"), include_currency=False) == "0.00"
    st.session_state.currency = "VND"


def test_low_stock_thresholds_per_unit():
    inv = pd.DataFrame({"Name": list("abcdef"), "Quantity": [250, 0.2, 2, 150, 5, 0.5],
                        "Unit": ["ml", "l", "kg", "g", "pcs", "l"]})
    assert utils.low_stock(inv, 10)["Name"].tolist() == ["a", "b", "e"]


def test_report_builds_and_sends():
    store.reset()
    subject, body = report.build_report(pd.Timestamp("2025-05-07").date())
    assert subject == "Theta Coffee Lab - 07 May: 363,750 VND, 2 orders"
    assert "6 x Iced Latte - Oat Milk" in body

    sent = []

    class FakeSMTP:
        def __init__(self, host, port): sent.append((host, port))
        def __enter__(self): return self
        def __exit__(self, *exc): pass
        def starttls(self): pass
        def login(self, user, password): pass
        def send_message(self, msg): sent.append(msg)

    env = {"SMTP_HOST": "smtp.example.com", "SMTP_USER": "cafe@example.com",
           "SMTP_PASSWORD": "x", "REPORT_TO": "owner@example.com"}
    old_smtp, old_env = report.smtplib.SMTP, dict(os.environ)
    report.smtplib.SMTP = FakeSMTP
    os.environ.update(env)
    try:
        report.send(subject, body)
    finally:
        report.smtplib.SMTP = old_smtp
        os.environ.clear()
        os.environ.update(old_env)
    assert sent[0] == ("smtp.example.com", 587) and sent[1]["To"] == "owner@example.com"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("ok")
