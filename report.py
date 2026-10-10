"""Daily sales and low-stock email report.

    python report.py --dry-run                 # print yesterday's report
    python report.py --date 2025-07-19         # send the report for one day

Sending reads SMTP_HOST, SMTP_PORT (default 587), SMTP_USER, SMTP_PASSWORD, and
REPORT_TO (comma-separated). Schedule it with cron, Windows Task Scheduler, or
any job runner that can reach the database (see README).
"""
import argparse
import datetime
import os
import smtplib
from email.message import EmailMessage

import pandas as pd

import store
import utils


def build_report(day, pcs_threshold=10.0):
    """Subject and plain-text body for one day's sales plus current low stock."""
    sales = store.load("sales")
    sales["Date"] = pd.to_datetime(sales["Date"], format="mixed")
    day_sales = sales[sales["Date"].dt.date == day]
    kpi = utils.sales_summary(day_sales, store.load("products"))
    low = utils.low_stock(store.load("inventory"), pcs_threshold)

    lines = [
        f"Theta Coffee Lab: daily report for {day:%A, %d %b %Y}",
        "",
        f"Revenue        {kpi['revenue']:>14,.0f} VND",
        f"Gross profit   {kpi['gross_profit']:>14,.0f} VND ({kpi['margin']:.1f}%)",
        f"Orders         {kpi['orders']:>14,}",
        f"Cups sold      {kpi['cups']:>14,}",
    ]
    if not day_sales.empty:
        top = day_sales.groupby("Product")["Quantity"].sum().nlargest(3)
        lines += ["", "Top products:"] + [f"  {q:>3} x {p}" for p, q in top.items()]
    lines += ["", f"Low stock ({len(low)} items):" if len(low) else "Stock: all items above their thresholds."]
    lines += [f"  {r.Name}: {r.Quantity:g} {r.Unit} (threshold {r.Threshold:g})" for r in low.itertuples()]

    subject = f"Theta Coffee Lab - {day:%d %b}: {kpi['revenue']:,.0f} VND, {kpi['orders']} orders"
    return subject, "\n".join(lines) + "\n"


def send(subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.environ["SMTP_USER"]
    msg["To"] = os.environ["REPORT_TO"]
    msg.set_content(body)
    with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.environ.get("SMTP_PORT", 587))) as smtp:
        smtp.starttls()
        smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        smtp.send_message(msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--date", type=datetime.date.fromisoformat,
                        default=datetime.date.today() - datetime.timedelta(days=1))
    parser.add_argument("--dry-run", action="store_true", help="print the report instead of emailing it")
    args = parser.parse_args()

    subject, body = build_report(args.date)
    if args.dry_run:
        print(subject, body, sep="\n\n")
    else:
        send(subject, body)
        print(f"Sent: {subject}")
