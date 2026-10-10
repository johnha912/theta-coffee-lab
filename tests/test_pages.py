"""Smoke test: every page renders against the bundled data without errors.

Run from the repo root: python -m pytest tests  (or: python tests/test_pages.py)
"""
import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
# A throwaway database seeded from data/*.csv, so tests never touch data/theta.db
os.environ.setdefault("DATABASE_URL", f"sqlite:///{tempfile.mkdtemp()}/test.db")
import utils  # noqa: E402


def test_sales_summary_matches_bundled_data():
    kpi = utils.sales_summary(pd.read_csv("data/sales.csv"), pd.read_csv("data/products.csv"))
    assert kpi['orders'] == 103 and kpi['cups'] == 289
    assert round(kpi['revenue']) == 5151447 and round(kpi['margin'], 2) == 44.83


def test_every_page_renders():
    for path in [ROOT / "app.py", *sorted(ROOT.glob("views/*.py"))]:
        at = AppTest.from_file(str(path), default_timeout=60)
        at.session_state.default_time_filter = "All Time"  # the bundled data is from 2025
        at.run()
        assert not at.exception, (path, at.exception)
        assert not at.error, (path, [e.value for e in at.error])


if __name__ == "__main__":
    test_sales_summary_matches_bundled_data()
    test_every_page_renders()
    print("ok")
