# yint.org link shortener

A small Django 5.2 LTS app: `yint.org/<source>` redirects to a stored destination and logs the
visit. It runs in Docker behind Caddy; Caddy serves `/static/` directly.

## Add or change a link

Log in at <https://yint.org/admin/> and open **Redirects**. `source` is the path after
`yint.org/`; `destination` is a full URL, or a path under `/static/`.

## Deploy an update

```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

Database migrations and `collectstatic` run each time the container starts.

## Check every link

```bash
docker exec yint-app python manage.py check_links
```

It sends each link through the app inside a transaction that is rolled back (no statistics
written) and reports wrong responses, links to missing files, and auto-created entries that
point to nothing. `--list-auto` lists those; `--delete-junk` deletes them.

## Files kept outside git

- `.env` (mode 600): `SECRET_KEY`, `DJANGO_DEBUG=0`, `POSTGRES_DB`, `POSTGRES_USER`,
  `POSTGRES_PASSWORD`. Both containers read it.
- `static/`: the site's own files (PDFs, media), served by Caddy and mounted into the app.

## Tests

```bash
SECRET_KEY=test DJANGO_DEBUG=1 python manage.py test
```
