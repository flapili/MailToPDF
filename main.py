import time
import quopri
import datetime
import email
import email.utils
import email.message
from uuid import uuid4
from pathlib import Path
from threading import Event
from imaplib import IMAP4_SSL

from croniter import croniter
from discord_webhook import DiscordWebhook
from playwright.sync_api import sync_playwright
from pydantic import BaseSettings, BaseModel, EmailStr, SecretStr, Field, validator, HttpUrl


class Settings(BaseSettings):
    server: str = Field(env="SERVER")
    user: EmailStr = Field(env="USER")
    pwd: SecretStr = Field(env="PWD")
    filter: str = Field("(UNSEEN)", env="FILTER")
    mailbox: str = Field("INBOX", env="MAILBOX")
    format: str = Field("{settings.mailbox}_{formatted_date}.pdf", env="FORMAT")
    date_format: str = Field("%Y_%m_%d_%Hh%Mm%Ss", env="DATE_FORMAT")
    cron_pattern: croniter | None = Field("*/1 * * * *", env="CRON_PATTERN")
    discord_webhook: HttpUrl | None = Field(None, env="DISCORD_WEBHOOK")

    @validator("cron_pattern", pre=True)
    def validate_cron_pattern(cls, v: str):
        if not v:
            return None
        return croniter(v)


class UIDS(BaseModel):
    uids: list[int]


def get_htmls(settings: Settings):
    conn = IMAP4_SSL(settings.server)
    conn.login(settings.user, settings.pwd.get_secret_value())
    conn.select()
    ret, data = conn.uid("search", None, settings.filter)
    if ret != "OK":
        raise NotImplementedError("TODO: handle error")

    uids = UIDS(uids=data[0].split()).uids
    if not uids:
        return []

    htmls: list[tuple[str, email.message.Message]] = []
    for uid in uids:
        ret, data = conn.uid("fetch", str(uid), "(RFC822)")
        if ret != "OK":
            raise NotImplementedError("TODO: handle error")

        msg = email.message_from_bytes(data[0][1])
        d: datetime.datetime = email.utils.parsedate_to_datetime(msg["Date"])
        msg["_formatted_date"] = d.strftime(settings.date_format)
        notification_msg = f"handling email : '{msg['Subject']}' from {msg['From']}"
        print(notification_msg)
        if settings.discord_webhook is not None:
            DiscordWebhook(str(settings.discord_webhook), content=notification_msg, rate_limit_retry=True).execute()

        for part in msg.walk():
            if part.get_content_type() == "text/html":
                p: str = part.get_payload()
                html = quopri.decodestring(p.encode("utf-8")).decode("utf-8")
                htmls.append((html, msg))

    conn.close()
    conn.logout()
    return htmls


def main(settings: Settings):
    with sync_playwright() as playwright:
        with playwright.chromium.launch() as browser:
            for html, msg in get_htmls(settings=settings):
                uuid = uuid4()
                p = Path("/") / "tmp" / "mail-screener" / f"{uuid}.html"
                p.parent.mkdir(parents=True, exist_ok=True)
                with p.open("w", encoding="utf-8") as f:
                    f.write(html)

                with browser.new_page() as page:
                    page.goto(f"file://{p}")

                    path = (
                        Path("/")
                        / "data"
                        / settings.format.format(msg=msg, settings=settings, formatted_date=msg["_formatted_date"])
                    )
                    page.pdf(path=path)


if __name__ == "__main__":
    import signal

    e = Event()

    def quit(signo, _frame):
        e.set()

    for sig in signal.SIGTERM, signal.SIGHUP, signal.SIGINT:
        signal.signal(sig, quit)

    settings = Settings()
    main(settings=settings)
    if settings.cron_pattern is not None:
        while not e.is_set():
            time_to_wait: float = settings.cron_pattern.get_next(ret_type=float) - time.time()
            if time_to_wait > 0:
                print(f"waiting for {time_to_wait:.3f}s")
                e.wait(time_to_wait)
            main(settings=settings)
