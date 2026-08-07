# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

`jenkins_jobs` is a small Python 3.11+ CLI package that talks to a Jenkins server (or a locally
cached snapshot of one) and reports information about each job — name, job type, description,
and whether/how it's timer-triggered — as pipe-separated (`|`) CSV lines. It exists because
neither the Jenkins CLI nor the raw REST API give a usable summary of jobs across a large Jenkins
instance, and the plugin-specific job XML formats are otherwise undocumented and inconsistent.

Packaging/dependency management uses `uv` and a PEP 621 `pyproject.toml` (build backend:
`uv_build`); there is no `setup.py`/`setup.cfg` or `requirements*.txt` anymore. Runtime
dependencies live in `[project.dependencies]`, dev-only ones (pytest, ruff, coverage, Sphinx,
tox, bump2version) in the `dev` extra (`[project.optional-dependencies]`) — install both with
`uv sync --extra dev`. `uv.lock` pins the resolved graph and should be committed.

Two console scripts are installed (see `[project.scripts]` in `pyproject.toml`):

* `jenkins_jobs` (`jenkins_jobs.reporter:main`) — connects to a Jenkins server (`--user`/`--token`/
  `--jenkins`) or reads a shelve-format snapshot (`--shelve-file`, mutually exclusive with the REST
  options) and reports one line per job, either as pipe CSV printed to stdout (`--format csv`,
  the default) or as a self-contained HTML5 report with a Chart.js bar chart of job counts by
  type, written to `./report.html` (`--format html`).
* `jenkins_exporter` (`jenkins_jobs.exporter:main`) — connects to a Jenkins server over the REST
  API and dumps every job's raw config (parsed from XML) into a local Python `shelve` file
  (`./jenkins_jobs.shelve`), so it can be replayed locally without hitting the server again.

## Commands

```bash
make lint          # uv run ruff check src/jenkins_jobs tests
make test          # uv run pytest -v (single Python version)
make test-all       # uv run tox (via tox-uv) — runs pytest across Python 3.11-3.14
make coverage       # coverage run + report + html, opens htmlcov/index.html
make docs           # regenerate Sphinx API docs and build HTML docs
```

Run a single test file or test:

```bash
uv run pytest tests/test_jobs.py
uv run pytest tests/test_jobs.py::test_clean_spec_crlf_multiple
```

CI (`.github/workflows/main.yml`) runs, for each supported Python version (3.11–3.14) via
`astral-sh/setup-uv`: a ruff syntax-error check (`--select=E9,F63,F7,F82`), a full `ruff check`
(warnings don't fail the build), `pytest`, and a `pip-audit` vulnerability scan of the resolved
project (`inputs: .`, reading `pyproject.toml`/`uv.lock`). Match this locally with `make lint`
and `make test` before pushing. `tox.ini` uses the `tox-uv` plugin (`runner =
uv-venv-lock-runner`) so tox environments are created and synced with `uv` instead of
virtualenv+pip.

Local development without hitting a real Jenkins server: pass `--shelve-file` pointing at a shelve
file produced by `jenkins_exporter` (or `make local`/`make debug`, which use `$DATA_SAMPLE`) and
`jenkins_jobs` will use `FileSystemRetriever` instead of `RESTRetriever`. `--shelve-file` is
mutually exclusive with `--user`/`--token`/`--jenkins` — `reporter.py`'s argparse setup puts the
two into separate argument groups and enforces the exclusivity/all-or-nothing rules itself after
`parse_args()`, since argparse's own `mutually_exclusive_group` can't express "all three or none
of this set, exclusive of that other option".

## Architecture

Source lives under `src/jenkins_jobs/` (the `uv_build` backend picks it up from `src/` by
default, matching the project name). Tests live in `tests/` and use fixture XML files in
`tests/raw_data/` (representative raw Jenkins job-config XML for each supported plugin, including
"bogus" variants for negative testing) via the `helpers.xml_config()` fixture defined in
`tests/conftest.py`.

The core flow is: **Retriever** (fetches raw job config) → **job factory** (picks a `JenkinsJob`
subclass based on structure) → **JenkinsJob instance** (parses description + timer trigger from
that job type's specific XML shape) → `str(job)` produces one report line.

* `retrievers.py` — `Retriever` (ABC) defines `all_jobs()` returning a generator function, plus
  the shared `_job_builder()` factory method that decides which `JenkinsJob` subclass to
  instantiate for a given job's parsed XML (dict, via `xmltodict`). Two concrete retrievers:
  `RESTRetriever` (live Jenkins server via the `python-jenkins` package) and
  `FileSystemRetriever` (reads a `shelve` file previously produced by `jenkins_exporter`). Both
  yield the same job objects, which is what lets `jenkins_jobs` transparently work against a
  cached snapshot instead of a live server.

* `jobs.py` — `JenkinsJob` (ABC) is the base for all job types; subclasses must implement
  `_find_desc(config)` and `_find_timer_trigger(config)` for their XML shape and get
  `one_line_desc()`, `_clean_spec()`, and `__str__()` (the pipe-CSV formatter) for free.
  `PluginBasedJob` is an intermediate ABC for jobs defined by a Jenkins plugin (detected by the
  presence of an `@plugin` attribute on the XML root); `PipelineJob` and `MavenJob` extend it.
  `FreestyleJob` extends `JenkinsJob` directly since freestyle jobs aren't plugin-based. Each
  subclass encodes where, in that job type's specific (and undocumented) nested dict structure,
  the description and `hudson.triggers.TimerTrigger` node live — this is the part of the codebase
  that's most sensitive to Jenkins/plugin XML changes. New job types are added here and then
  registered in `Retriever.plugin_based_jobs` (keyed by plugin name) or in `_job_builder()` for
  non-plugin cases.

* `exceptions.py` — all custom exceptions derive from `JenkinsJobError`. `MissingXMLElementError`
  and `InvalidXMLConfigError` are raised when the parsed job XML doesn't have the structure a
  `JenkinsJob` subclass expects (missing nodes are treated as data errors, not bugs, since the
  XML shape is plugin-controlled and not officially documented).

* `reporter.py` / `exporter.py` — thin argparse-based CLI entry points. `exporter.py` always
  requires `--user`/`--token`/`--jenkins`. `reporter.py` requires either those three together (REST
  mode) or `--shelve-file` alone (local snapshot mode); either way, when REST mode is used, the
  Jenkins URL is validated to have a schema (raising `NoSchemaSuppliedRESTError` otherwise, since a
  missing schema produces a confusing error deep inside `requests` instead).

XML is parsed with `xmltodict`, so job configs move through the codebase as nested `dict`/
`OrderedDict` structures mirroring the original XML — reading a fixture file in `tests/raw_data/`
alongside the corresponding job class is usually the fastest way to understand a given job type's
shape.
