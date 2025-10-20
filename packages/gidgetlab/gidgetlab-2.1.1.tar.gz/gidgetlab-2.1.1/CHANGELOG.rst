Changelog
=========

2.1.1 (2025-10-19)
------------------

* Drop python 3.9 support
* Test on python 3.14
* Switch from flake8/black to ruff

2.1.0 (2025-02-09)
------------------

* Add head method (thanks to John Marley)
* Drop python 3.8 support
* Test on python 3.13
* Remove twisted support

2.0.1 (2024-04-04)
------------------

* Fix params typing (should accept value of both str and bool)
* Update gitlab api clients link in README (thanks to Elan Ruusamäe)

2.0.0 (2024-02-21)
------------------

* Use OAuth-compliant headers for access token
  (allow to use Oauth 2.0 tokens as well as personal/group/project token)
* Move from setup.py to pyproject.toml
* Add Python 3.12 tests
* Drop Python 3.6 and 3.7 support
* Fix deprecation warnings (remove cgi and pkg_resources)

1.1.0 (2023-10-20)
------------------

* Add GraphQL support
* Add python:3.11 tests

1.0.0 (2022-03-04)
------------------

* Support binary in response body (thanks to Ugur Yilmaz)
* Add python:3.10 tests
* Improve packaging

0.7.0 (2021-08-19)
------------------

* Add possibility to set gitlab url via GL_URL env var (thanks to Michael Aigner)
* Fix KeyError when x-gitlab-event is missing
* Pin treq to < 21
* Fix copyright in docs (thanks to Mariatta)
* Add Python 3.9 tests

0.6.0 (2020-05-18)
------------------

* Add httpx support
* Add Python 3.8 tests
* Move tests outside package to fix coverage
* Add pipeline, coverage and pre-commit badges
* Add py.typed file (PEP 561)
* Switch to RTD's default theme

0.5.0 (2019-07-08)
------------------

* Allow to pass an optional SSLContext to GitLabBot (thanks to Clément Moyroud)
* Allow the bot to not wait for consistency

0.4.0 (2019-05-20)
------------------

* Add 202 as expected response from GitLab
* Fix mypy warnings about the ``Dict`` and ``Mapping`` generic types lacking
  type parameters (taken from gidgethub)
* Add /health endpoint to the bot

0.3.1 (2019-04-17)
------------------

* Allow to pass any keyword arguments to aiohttp.web.run_app()
  from bot.run() to configure port, logging...
* Improve documentation (thanks to Jon McKenzie)

0.3.0 (2018-08-21)
------------------

* Add a GitLabBot class

0.2.0 (2018-08-18)
------------------

* Replace URI template with query string params

0.1.0 (2018-07-22)
------------------

* Initial release
