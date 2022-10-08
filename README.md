# MailScreener by flapili

## Usage

### Build
`docker build -t mailscrenner .`

### run
```
docker run --rm -v $PWD/output:/data \
-e SERVER="mail.foo.bar" \
-e USER="foo@bar.baz" \
-e PWD="my password" \
-e FILTER="ALL" \
-e DISCORD_WEBHOOK="https://discord.com/api/webhooks/123456789/azertyuiop" \
mailscreener```