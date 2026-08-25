# Sandbox

Personal sandbox for data analysis experiments, with parallel Python and R
toolchains that both talk to a local PostgreSQL + ClickHouse stack.

## Using this as a template

This repo is set up to be used via GitHub's **Use this template** button. After
creating your copy:

1. Rename the project: `name` in `pyproject.toml`, the `sandbox/` package
   directory, and the `sandbox = "sandbox:main"` entry point in
   `[project.scripts]`.
2. Update `DB_NAME`/`CLICKHOUSE_DB` defaults in `.env.example` and
   `docker-compose.yml` if you don't want `sandbox_dev` as the database name.
3. Replace this README's content with a description of your actual project.
4. Update the copyright line in `LICENSE`, or replace it with your own license.

### Starting fresh: delete the local copy, create a new repo, re-provision

To throw away a local clone of this repo and start a clean copy from the
template:

1. **Stop and remove the local containers**, then delete the local clone:
   ```sh
   cd ~/projects/<old-clone-dir>
   docker compose down -v
   cd ..
   rm -rf <old-clone-dir>
   ```
   `docker compose down -v` also drops the `postgres_data`/`clickhouse_data`
   volumes, so the old containers don't linger with stale data/ports.

2. **Create the new repository from the template** on GitHub: make sure
   *Settings → General → Template repository* is enabled on the source repo,
   then click **Use this template → Create a new repository**, pick a name
   and visibility. This produces a new repo with a single clean commit (no
   history from the source repo).

3. **Clone the new repository**:
   ```sh
   git clone https://github.com/<owner>/<new-repo>.git
   cd <new-repo>
   ```

4. **Re-provision the environment**:
   ```sh
   docker compose up -d
   uv sync
   cp .env.example .env
   ```
   If port `5432` (or `8123`/`9000`) is already taken on your machine, change
   `DB_PORT` (or the `CLICKHOUSE_*_PORT` vars) in `.env` before starting the
   containers.
   ```sh
   uv run sandbox                                   # check the Postgres connection
   uv run python scripts/python/clickhouse_check.py # check the ClickHouse connection
   uv run python scripts/python/generate_data.py    # load the synthetic dataset
   ```
   ```r
   renv::restore()
   ```

## Stack

- Python 3.13, managed with [uv](https://docs.astral.sh/uv/) (`pyproject.toml` / `uv.lock`)
- R, managed with [renv](https://rstudio.github.io/renv/) (`renv.lock`)
- PostgreSQL and ClickHouse, run locally via Docker Compose (`duckdb` is also
  available for local/embedded analysis)

## Setup

### Databases

```sh
docker compose up -d
```

Starts local Postgres (`localhost:5432`) and ClickHouse
(`localhost:8123` HTTP / `localhost:9000` native) containers with data
persisted in named Docker volumes.

### Python

```sh
uv sync
```

### R

```r
renv::restore()
```

### Environment variables

Both toolchains and `docker-compose.yml` read connection settings from
environment variables: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`,
`DB_PASSWORD` for Postgres, and `CLICKHOUSE_HOST`, `CLICKHOUSE_HTTP_PORT`,
`CLICKHOUSE_TCP_PORT`, `CLICKHOUSE_DB`, `CLICKHOUSE_USER`,
`CLICKHOUSE_PASSWORD` for ClickHouse.

- Python and Docker Compose load them from a `.env` file (see `.env.example`).
- R loads the Postgres variables from a `.Renviron` file (same variable names).

Copy `.env.example` to `.env` (and/or `.Renviron`) before starting the
containers.

## Usage

```sh
docker compose up -d                            # start Postgres + ClickHouse
uv run sandbox                                   # check the Postgres connection
uv run python scripts/python/db_check.py         # check the Postgres connection
uv run python scripts/python/clickhouse_check.py # check the ClickHouse connection
uv run python scripts/python/generate_data.py    # generate & load a synthetic
                                                  # users/events dataset into
                                                  # both databases
Rscript scripts/r/db_check.R
```
