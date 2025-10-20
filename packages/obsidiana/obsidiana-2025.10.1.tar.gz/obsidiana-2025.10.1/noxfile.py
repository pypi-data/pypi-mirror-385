from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
import os
import subprocess

import nox

ROOT = Path(__file__).parent
PYPROJECT = ROOT / "pyproject.toml"
PACKAGE = ROOT / "obsidiana"


PYTHON = "3.13"

nox.options.default_venv_backend = "uv"
nox.options.sessions = []


def session(default=True, python=PYTHON, **kwargs):  # noqa: D103
    def _session(fn):
        if default:
            nox.options.sessions.append(kwargs.get("name", fn.__name__))
        return nox.session(python=python, **kwargs)(fn)

    return _session


@session()
def tests(session):
    """
    Run the test suite.
    """
    session.install("pytest")

    if session.posargs and session.posargs[0] == "coverage":
        if len(session.posargs) > 1 and session.posargs[1] == "github":
            github = Path(os.environ["GITHUB_STEP_SUMMARY"])
        else:
            github = None

        session.install("coverage[toml]")
        session.run("coverage", "run", "-m", "pytest", PACKAGE)
        if github is None:
            session.run("coverage", "report")
        else:
            with github.open("a") as summary:
                summary.write("### Coverage\n\n")
                summary.flush()  # without a flush, output seems out of order.
                session.run(
                    "coverage",
                    "report",
                    "--format=markdown",
                    stdout=summary,
                )
    else:
        session.run("python", "-m", "pytest", *session.posargs, PACKAGE)


@session()
def audit(session):
    """
    Audit Python dependencies for vulnerabilities.
    """
    session.install("pip-audit")
    with NamedTemporaryFile() as tmpfile:
        subprocess.run(
            ["uv", "pip", "freeze"],  # noqa: S607
            cwd=ROOT,
            check=True,
            stdout=tmpfile,
        )
        session.run("python", "-m", "pip_audit", "-r", tmpfile.name)


@session(tags=["build"])
def build(session):
    """
    Build a distribution suitable for PyPI and check its validity.
    """
    session.install("build[uv]", "twine")
    with TemporaryDirectory() as tmpdir:
        session.run(
            "pyproject-build",
            "--installer=uv",
            ROOT,
            "--outdir",
            tmpdir,
        )
        session.run("twine", "check", "--strict", tmpdir + "/*")


@session(tags=["style"])
def style(session):
    """
    Check for coding style.
    """
    session.install("ruff")
    session.run("ruff", "check", ROOT, __file__)
