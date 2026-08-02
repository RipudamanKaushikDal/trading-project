## Objective

Hobby project to build a full scale trading bot using latest tech stack, ai algos and software development best practices.

`Goal: Write all the code manually with clear intention and understanding`

## Backfill Last Year

Run the one-year historical backfill with:

```bash
python app/run_backfill.py
```

Notes:

- The script writes candles per symbol using the session manager in `repositories/db.py`.
- Timeframe is currently set to `TIMEFRAME.HOUR_1` in `app/run_backfill.py`.
- Configure `DATABASE_URL` in your environment before running.
