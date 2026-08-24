# Project Guidelines

## Project Shape
- This is a Python package for the Linode Metadata Service. Runtime code lives in [linode_metadata](linode_metadata), unit tests in [test/unit](test/unit), Linode-backed integration tests in [test/integration](test/integration), and Sphinx docs in [docs](docs).
- Use [README.md](README.md) for installation, usage, and end-to-end testing details; use [CONTRIBUTING.md](CONTRIBUTING.md) for contribution expectations.
- Treat [build](build), [docs/_build](docs/_build), and [linode_metadata.egg-info](linode_metadata.egg-info) as generated artifacts unless the task explicitly concerns packaging output.

## Architecture
- [linode_metadata/metadata_client.py](linode_metadata/metadata_client.py) owns the sync and async clients, shared HTTP request preparation, token generation/refresh, response parsing, and metadata endpoint methods. Keep `MetadataClient` and `AsyncMetadataClient` behavior in sync when changing client semantics.
- [linode_metadata/watcher.py](linode_metadata/watcher.py) mirrors sync generators and async generators for polling metadata. Watchers yield immediately, then only when `dataclasses.asdict()` differs from the previous response.
- [linode_metadata/objects](linode_metadata/objects) contains lightweight dataclass response wrappers. Classes usually inherit `ResponseBase` with `@dataclass(init=False)`; use `field(metadata={"json": "service_key"})` when the service key differs from the Python attribute.
- Public imports are re-exported from [linode_metadata/__init__.py](linode_metadata/__init__.py); update it only when the public surface changes.

## Build And Test
- Install dev dependencies with `make dev-install`; this also regenerates [linode_metadata/version.py](linode_metadata/version.py) through the `create-version` target.
- Run fast local checks with `make unit-test` and `make lint`. Use `make format` to run Black, isort, and autoflake.
- Run `make build` for packaging checks. The package supports Python `>=3.9` and configures Black/isort line length at 80 in [pyproject.toml](pyproject.toml).
- Integration tests require the Metadata Service from inside a Linode or Ansible-provisioned test infrastructure. Do not run `make int-test`, `make int-test-local`, or `make test` unless the user asks for integration coverage and the required `LINODE_TOKEN`/environment is available.

## Coding Conventions
- Preserve sync/async parity: new client endpoints, token behavior, errors, and watcher changes normally need both synchronous and asynchronous implementations plus matching tests.
- Prefer existing `ResponseBase` population behavior for new response objects instead of hand-parsing JSON. Add focused unit tests under [test/unit/objects](test/unit/objects) for object mapping changes.
- Keep request behavior centralized in `BaseMetadataClient` helpers where practical so headers, user agent, timeouts, error handling, and debug logging stay consistent.
- Update Sphinx `.rst` files under [docs/linode_metadata](docs/linode_metadata) when public classes, methods, or response objects change.

## Test Notes
- Unit tests use pytest and mostly validate response object mapping without network access.
- Integration tests use session-scoped sync and async clients from [test/integration/conftest.py](test/integration/conftest.py), include an autouse 5-second delay to avoid 429s, and exercise real Metadata Service behavior.
- When changing integration assertions, reuse or extend helpers in [test/integration/helpers.py](test/integration/helpers.py) so sync and async tests keep consistent expectations.

## Maintaining This File
- Keep this file factually accurate. If an agent finds a statement here that is demonstrably incorrect, or makes a code, configuration, or workflow change that invalidates it, update [AGENTS.md](AGENTS.md) in the same change.
- Limit maintenance edits to durable, repository-wide guidance affected by the discovery or change; do not add speculative rules or transient implementation details.
