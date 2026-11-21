# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

`jenkins_jobs` is a small Python 3.11+ CLI package that talks to a Jenkins server (or a locally
cached snapshot of one) and reports information about each job — name, job type, description,
and whether/how it's timer-triggered. It exists because neither the Jenkins CLI nor the raw REST
API give a usable summary of jobs across a large Jenkins instance, and the plugin-specific job XML
formats are otherwise undocumented and inconsistent.

Packaging/dependency management uses `uv` and a PEP 621 `pyproject.toml` (build backend:
`uv_build`); there is no `setup.py`/`setup.cfg` or `requirements*.txt`. Runtime dependencies live
in `[project.dependencies]`, dev-only ones (pytest, ruff, coverage, Sphinx, tox, tox-uv-bare,
bump2version) in the `dev` extra — install both with `uv sync --extra dev` (or `make init`).
`uv.lock` pins the resolved graph and should be committed. Dev deps are deliberately kept in
`[project.optional-dependencies]` rather than PEP 735 `[dependency-groups]` so Dependabot's pip
ecosystem can see and bump them — don't migrate them.

Two console scripts are installed (`[project.scripts]` — note the **hyphenated** names):

* `jenkins-jobs` (`jenkins_jobs.reporter:main`) — connects to a Jenkins server
  (`--user`/`--token`/`--jenkins`) or reads a shelve-format snapshot (`--shelve-file`, mutually
  exclusive with the REST options) and writes a report to the current directory: `./report.csv`
  (`--format csv`, the default; pipe-separated, one line per job) or `./report.html`
  (`--format html`; self-contained HTML5 with a Chart.js bar chart of job counts by type, Chart.js
  loaded from a CDN).
* `jenkins-exporter` (`jenkins_jobs.exporter:main`) — connects to a Jenkins server over the REST
  API and dumps every job's raw config (parsed from XML) into a local Python `shelve` file
  (`./jenkins_jobs.shelve`), so it can be replayed locally without hitting the server again.

## Commands

```bash
make init           # uv venv + uv sync --extra dev
make lint           # uv run ruff check src/jenkins_jobs tests
make test           # uv run pytest -v (single Python version)
make test-all       # uv run tox (via tox-uv) — runs pytest across Python 3.11-3.14
make coverage       # coverage run + report + html, opens htmlcov/index.html
make docs           # regenerate Sphinx API docs (sphinx-apidoc) and build HTML docs
make dist           # uv build
make update-deps    # uv lock --upgrade + resync
```

Run a single test file or test (run from the repo root — the `helpers.xml_config()` fixture opens
`tests/raw_data/<file>` with a relative path):

```bash
uv run pytest tests/test_jobs.py
uv run pytest tests/test_jobs.py::test_clean_spec_crlf_multiple
```

Ruff config is in `pyproject.toml` (line length 127, rules `E,F,W,C90`, max complexity 10, `docs/`
excluded). CI (`.github/workflows/main.yml`) runs, for each Python 3.11–3.14 via
`astral-sh/setup-uv`: `ruff check . --select=E9,F63,F7,F82` (fails the build), a full
`ruff check . --exit-zero` (warnings only), `pytest`, and a `pip-audit` scan of the project.
Match this locally with `make lint` and `make test` before pushing. `tox.ini` uses the
`tox-uv-bare` plugin (`runner = uv-venv-lock-runner`), relying on the system `uv`.

Local development without a real Jenkins server: pass `--shelve-file` pointing at a shelve file
produced by `jenkins-exporter`, e.g. `uv run jenkins-jobs --shelve-file ./jenkins_jobs.shelve`.
`make local`/`make debug` (pdb) do the same using `DATA_SAMPLE=<path>` passed on the `make` command
line. `reporter.py` puts the REST options and `--shelve-file` in separate argparse groups and
enforces the exclusivity / all-three-or-none rules itself after `parse_args()`, since argparse's
`mutually_exclusive_group` can't express that.

## Architecture

Source lives under `src/jenkins_jobs/`; tests in `tests/` use fixture XML files in
`tests/raw_data/` (representative raw Jenkins job-config XML for each supported job type,
including "bogus" variants for negative testing) via the `helpers.xml_config()` fixture in
`tests/conftest.py`.

The core flow is: **Retriever** (fetches raw job config) → **job factory** (picks a `JenkinsJob`
subclass based on XML structure) → **JenkinsJob instances** (parse description + timer trigger
from that job type's XML shape) → **ReportFormatter** (turns the jobs into CSV or HTML).

* `retrievers.py` — `Retriever` (ABC) defines `all_jobs()`, which **returns a generator
  function** (callers do `jobs = retriever.all_jobs(); jobs()`), plus the shared `_job_builder()`
  factory: a root `project` key → `FreestyleJob`; otherwise the root's `@plugin` attribute is
  looked up in `Retriever.plugin_based_jobs` (`workflow-job` → `PipelineJob`, `maven-plugin` →
  `MavenJob`). Unknown plugins raise `UnknownJobTypeError`; other missing keys raise
  `InvalidXMLConfigError`. `RESTRetriever` uses `python-jenkins`; `FileSystemRetriever` reads the
  shelve produced by the exporter. Both yield the same job objects.

* `jobs.py` — `JenkinsJob` (ABC) is the base for all job types; subclasses implement
  `_find_desc(config)` and `_find_timer_trigger(config)` (the latter returns a
  `TimerTriggerResult`) and inherit `one_line_desc()`, `_clean_spec()`, and `__str__()` (the
  pipe-CSV line). `PluginBasedJob` is an intermediate ABC for plugin-defined jobs; `PipelineJob`
  and `MavenJob` extend it. `FreestyleJob` extends `JenkinsJob` directly. Each subclass encodes
  where, in its undocumented nested dict structure, the description and
  `hudson.triggers.TimerTrigger` node live — the part of the codebase most sensitive to
  Jenkins/plugin XML changes. To add a job type: subclass here, register it in
  `Retriever.plugin_based_jobs` (or `_job_builder()` for non-plugin cases), and add fixture XML
  (plus a bogus variant) to `tests/raw_data/`.

* `formatters.py` — `ReportFormatter` (ABC) with `generate(jobs) -> str`. `CSVFormatter` joins
  `str(job)` lines; `HTMLFormatter` renders a `string.Template` page, groups counts by
  `job.__class__.__name__`, and HTML-escapes every value. The `FORMATTERS` dict maps `--format`
  values to classes and also drives the argparse `choices`, so a new format only needs a subclass
  plus a `FORMATTERS` entry (and an output-file branch in `reporter.py`).

* `exceptions.py` — all custom exceptions derive from `JenkinsJobError`. Missing XML nodes are
  treated as data errors (`MissingXMLElementError`, `InvalidXMLConfigError`), not bugs, since the
  XML shape is plugin-controlled.

* `reporter.py` / `exporter.py` — thin argparse CLI entry points (`main()` is marked
  `# pragma: no cover`). In REST mode both reject a `--jenkins` URL without an `http` schema by
  raising `NoSchemaSuppliedRESTError`, since a missing schema otherwise fails confusingly deep
  inside `requests`.

XML is parsed with `xmltodict`, so job configs move through the codebase as nested `dict`
structures mirroring the original XML — reading a fixture in `tests/raw_data/` alongside the
corresponding job class is usually the fastest way to understand a job type's shape.
