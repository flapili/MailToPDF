# MailToPDF by flapili



## Usage

### Build
`docker build -t mailtopdf .`

### run
MailToPDF use environnment variable for configuration:

| variable name   | default value                           | required | example                                                   |
|-----------------|-----------------------------------------|----------|-----------------------------------------------------------|
| SERVER          | ...                                     | yes      | mail.example.com                                          |
| USER            | ...                                     | yes      | user@example.com                                          |
| PWD             | ...                                     | yes      | P@SSW0RD                                                  |
| FILTER          | (UNSEEN)                                | no       | (FROM "foo@example.com" SUBJECT "my subject" UNSEEN)      |
| MAILBOX         | INBOX                                   | no       | OUTBOX                                                    |
| FORMAT          | {settings.mailbox}_{formatted_date}.pdf | no       | PDF_from_mailToPdf{settings.mailbox}_{formatted_date}.pdf |
| DATE_FORMAT     | %Y_%m_%d_%Hh%Mm%Ss                      | no       | %Y_%m_%d_%Hh%Mm%Ss                                        |
| CRON_PATTERN    | /1 * * *                                | no       | /5 * * *                                                  |
| DISCORD_WEBHOOK | ...                                     | no       | https://discord.com/api/webhooks/123456789/azertyuiop     |

... mean there is no default value

pass an empty string to CRON_PATTERN to disable loop pooling

#### example

```
docker run --rm -v $PWD/output:/data \
-e SERVER="mail.foo.bar" \
-e USER="foo@bar.baz" \
-e PWD="my password" \
-e FILTER="ALL" \
-e DISCORD_WEBHOOK="https://discord.com/api/webhooks/123456789/azertyuiop" \
mailtopdf```

