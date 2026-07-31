from __future__ import annotations

import argparse
import datetime as dt
import html
import logging
import os
import smtplib
import sys
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SQL_FILE = BASE_DIR / "sql" / "tablespace_usage.sql"


@dataclass(frozen=True)
class TablespaceUsage:
    name: str
    contents: str
    status: str
    used_percent: float
    used_mb: float
    max_mb: float


@dataclass(frozen=True)
class MailConfig:
    host: str
    port: int
    user: str
    password: str
    use_tls: bool
    mail_from: str
    mail_to: list[str]


def main() -> int:
    parser = argparse.ArgumentParser(description="Send Oracle tablespace usage report by email.")
    parser.add_argument("--sample", action="store_true", help="Use sample tablespace rows instead of Oracle.")
    parser.add_argument("--dry-run", action="store_true", help="Print the email instead of sending it.")
    args = parser.parse_args()

    load_env(BASE_DIR / ".env")
    setup_logging(os.getenv("LOG_FILE", "logs/tablespace-monitor.log"))

    warning_percent = get_float_env("WARNING_PERCENT", 80.0)
    critical_percent = get_float_env("CRITICAL_PERCENT", 90.0)
    mail_always = get_bool_env("MAIL_ALWAYS", True)

    try:
        rows = sample_rows() if args.sample else fetch_tablespace_usage()
        status = overall_status(rows, warning_percent, critical_percent)
        subject = build_subject(status)
        text_body = build_text_body(rows, warning_percent, critical_percent)
        html_body = build_html_body(rows, warning_percent, critical_percent)

        should_send = mail_always or status != "OK"
        if args.dry_run or not should_send:
            print(subject)
            print()
            print(text_body)
            if not should_send:
                logging.info("No alert rows found. MAIL_ALWAYS=false, so email was not sent.")
            return 0

        send_mail(load_mail_config(), subject, text_body, html_body)
        logging.info("Tablespace report sent. status=%s rows=%s", status, len(rows))
        return 0
    except Exception:
        logging.exception("Tablespace monitor failed.")
        raise


def load_env(path: Path) -> None:
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def setup_logging(log_file: str) -> None:
    path = BASE_DIR / log_file
    path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=path,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        encoding="utf-8",
    )


def fetch_tablespace_usage() -> list[TablespaceUsage]:
    try:
        import oracledb
    except ImportError as exc:
        raise RuntimeError("oracledb is not installed. Run: pip install -r requirements.txt") from exc

    required = ["ORACLE_USER", "ORACLE_PASSWORD", "ORACLE_DSN"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError("Missing Oracle settings: " + ", ".join(missing))

    sql = SQL_FILE.read_text(encoding="utf-8")
    with oracledb.connect(
        user=os.environ["ORACLE_USER"],
        password=os.environ["ORACLE_PASSWORD"],
        dsn=os.environ["ORACLE_DSN"],
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            return [
                TablespaceUsage(
                    name=str(row[0]),
                    contents=str(row[1]),
                    status=str(row[2]),
                    used_percent=float(row[3]),
                    used_mb=float(row[4]),
                    max_mb=float(row[5]),
                )
                for row in cursor
            ]


def sample_rows() -> list[TablespaceUsage]:
    return [
        TablespaceUsage("USERS", "PERMANENT", "ONLINE", 64.2, 6420.0, 10000.0),
        TablespaceUsage("APP_DATA", "PERMANENT", "ONLINE", 84.7, 16940.0, 20000.0),
        TablespaceUsage("APP_INDEX", "PERMANENT", "ONLINE", 72.1, 7210.0, 10000.0),
        TablespaceUsage("TEMP", "TEMPORARY", "ONLINE", 91.3, 9130.0, 10000.0),
        TablespaceUsage("UNDOTBS1", "UNDO", "ONLINE", 43.5, 4350.0, 10000.0),
    ]


def overall_status(rows: list[TablespaceUsage], warning_percent: float, critical_percent: float) -> str:
    if any(row.used_percent >= critical_percent for row in rows):
        return "CRITICAL"
    if any(row.used_percent >= warning_percent for row in rows):
        return "WARNING"
    return "OK"


def row_status(row: TablespaceUsage, warning_percent: float, critical_percent: float) -> str:
    if row.used_percent >= critical_percent:
        return "CRITICAL"
    if row.used_percent >= warning_percent:
        return "WARNING"
    return "OK"


def build_subject(status: str) -> str:
    today = dt.date.today().isoformat()
    return f"[{status}] Oracle tablespace usage report {today}"


def build_text_body(rows: list[TablespaceUsage], warning_percent: float, critical_percent: float) -> str:
    lines = [
        "Oracle tablespace usage report",
        f"Checked at: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Warning: {warning_percent:.1f}% / Critical: {critical_percent:.1f}%",
        "",
        "status     tablespace             contents    used%      used_mb      max_mb",
        "---------  ---------------------  ----------  ------  -----------  ----------",
    ]
    for row in rows:
        status = row_status(row, warning_percent, critical_percent)
        lines.append(
            f"{status:<9}  {row.name:<21}  {row.contents:<10}  "
            f"{row.used_percent:>6.1f}  {row.used_mb:>11.1f}  {row.max_mb:>10.1f}"
        )
    return "\n".join(lines)


def build_html_body(rows: list[TablespaceUsage], warning_percent: float, critical_percent: float) -> str:
    body_rows = []
    for row in rows:
        status = row_status(row, warning_percent, critical_percent)
        color = {"OK": "#e8f5e9", "WARNING": "#fff8e1", "CRITICAL": "#ffebee"}[status]
        body_rows.append(
            "<tr>"
            f"<td style='background:{color}'>{html.escape(status)}</td>"
            f"<td>{html.escape(row.name)}</td>"
            f"<td>{html.escape(row.contents)}</td>"
            f"<td>{html.escape(row.status)}</td>"
            f"<td style='text-align:right'>{row.used_percent:.1f}</td>"
            f"<td style='text-align:right'>{row.used_mb:.1f}</td>"
            f"<td style='text-align:right'>{row.max_mb:.1f}</td>"
            "</tr>"
        )

    return (
        "<html><body>"
        "<h2>Oracle tablespace usage report</h2>"
        f"<p>Checked at: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
        f"<p>Warning: {warning_percent:.1f}% / Critical: {critical_percent:.1f}%</p>"
        "<table border='1' cellpadding='6' cellspacing='0'>"
        "<thead><tr>"
        "<th>Status</th><th>Tablespace</th><th>Contents</th><th>DB Status</th>"
        "<th>Used %</th><th>Used MB</th><th>Max MB</th>"
        "</tr></thead><tbody>"
        + "".join(body_rows)
        + "</tbody></table></body></html>"
    )


def load_mail_config() -> MailConfig:
    required = ["SMTP_HOST", "SMTP_PORT", "MAIL_FROM", "MAIL_TO"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError("Missing mail settings: " + ", ".join(missing))

    return MailConfig(
        host=os.environ["SMTP_HOST"],
        port=int(os.environ["SMTP_PORT"]),
        user=os.getenv("SMTP_USER", ""),
        password=os.getenv("SMTP_PASSWORD", ""),
        use_tls=get_bool_env("SMTP_USE_TLS", True),
        mail_from=os.environ["MAIL_FROM"],
        mail_to=[item.strip() for item in os.environ["MAIL_TO"].split(",") if item.strip()],
    )


def send_mail(config: MailConfig, subject: str, text_body: str, html_body: str) -> None:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = config.mail_from
    message["To"] = ", ".join(config.mail_to)
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(config.host, config.port, timeout=30) as smtp:
        if config.use_tls:
            smtp.starttls()
        if config.user:
            smtp.login(config.user, config.password)
        smtp.send_message(message)


def get_bool_env(key: str, default: bool) -> bool:
    value = os.getenv(key)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_float_env(key: str, default: float) -> float:
    value = os.getenv(key)
    if value is None:
        return default
    return float(value)


if __name__ == "__main__":
    sys.exit(main())
