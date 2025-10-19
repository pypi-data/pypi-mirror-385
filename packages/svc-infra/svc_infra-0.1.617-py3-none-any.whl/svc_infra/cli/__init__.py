from __future__ import annotations

import typer

from svc_infra.cli.cmds import (
    _HELP,
    jobs_app,
    register_alembic,
    register_docs,
    register_dx,
    register_mongo,
    register_mongo_scaffold,
    register_obs,
    register_sdk,
    register_sql_export,
    register_sql_scaffold,
)
from svc_infra.cli.foundation.typer_bootstrap import pre_cli

app = typer.Typer(no_args_is_help=True, add_completion=False, help=_HELP)
pre_cli(app)

# --- sql commands ---
register_alembic(app)
register_sql_scaffold(app)
register_sql_export(app)

# --- nosql commands ---
register_mongo(app)
register_mongo_scaffold(app)

# -- observability commands ---
register_obs(app)

# -- dx commands ---
register_dx(app)

# -- jobs commands ---
app.add_typer(jobs_app, name="jobs")

# -- sdk commands ---
register_sdk(app)

# -- docs commands ---
register_docs(app)


def main():
    app()


if __name__ == "__main__":
    main()
