# Rock and Fluid Sample (RAFS) DDMS

## Introduction

Rock and Fluid Sample Domain Data Management Services (RAFS DDMS) Open Subsurface Data Universe (OSDU) is a microservices-based project that comprises OSDU software ecosystem, written in Python that provides an API for Rock and Fluid Sample related data.

[[_TOC_]]

## Project structure

    app
    ├── api              - web related stuff.
    │   ├── dependencies - dependencies for routes definition.
    │   ├── errors       - definition of error handlers.
    │   └── routes       - web routes.
    ├── core             - application configuration, startup events, logging.
    ├── db               - db related stuff.
    ├── models           - pydantic models for this application.
    │   ├── domain       - main models that are related to the rock and fluid samples domain
    │   └── schemas      - schemas for using in web routes (request, responses bodies).
    ├── resources        - any useful blob/file or constants
    ├── services         - logic that is not just crud related.
    └── main.py          - FastAPI application creation and configuration.

## Project Tutorial

Instructions and payload examples are presented on [the tutorial page](./docs/tutorial/readme.md).

## API Specs

Compiled REST API documentation is presented in the [openapi.json](./docs/spec/openapi.json) file.

## OSDU Well Known Schemas Disclaimer

Note regarding OSDU Well Known Schema interaction: Currently (April 2023), OSDU Data Definitions "Fluid Samples" and "Samples & Petrophysics" Project teams are re-working the data model for both rock and fluid samples in a way that there will be a unified way to handle both. That means that today there are no FluidSample, FluidSampleAnalysis, or FluidSampleAcquisition schemas published by OSDU Data Definitions, which can be used by the DDMS. Similarly, it is likely that RockSample, RockSampleAnalysis, and Coring schemas will be changed by the Forum or even be deprecated and replaced in the near future. In light of this: 1) With regard to PVT, the RAFS DDMS currently uses custom WPC and Master schemas 2) With regard to RCA, the DDMS does have relationship to the existing rock-related schemas mentioned above. In both cases, the DDMS will need to be updated when the revised OSDU Data Definitions data model is published. 

## Project Startup
### Configuration

The settings module can read environment variables as long as they are declared as fields of the
Settings class (see app/core/settings/base.py).

Or they can be provided in a .env or prod.env files

#### Python Version
RAFS DDMS runs in **Python 3.11**.  <br/>
> **NOTE:** The pip install will not currently work on Windows.  Requires a Linux machine (or Container).

#### Local settings

Add an .env with:

```
APP_ENV="dev"
OPENAPI_PREFIX="/api/os-rafs-ddms"  # optional
CLOUD_PROVIDER="azure"
API_BASE_URL="osdu_endpoint"
SERVICE_HOST_DATASET="${API_BASE_URL}/api/dataset/v1"
SERVICE_HOST_STORAGE="${API_BASE_URL}/api/storage/v2"
# Optionally add any other env var (BUILD_DATE, etc.)
```

#### Cache settings

It is needed to add the following variables to .env to set up cache layer:
```
CACHE_ENABLE=True
CACHE_BACKEND="app.core.helpers.cache.backends.redis_cache.RedisCacheBackend"
```

The `CACHE_ENABLE` variable can enable or disable cache for all app.
Besides, to disable caching in a request just use "Cache-Control" in a request header as "no-store" or "no-cache".

The `CACHE_BACKEND` variable is a path to your backend,
which is used to initialize FastAPICache like [here](https://github.com/long2ice/fastapi-cache#quick-start).

You can use already prepared backends like:
 * `app.core.helpers.cache.backends.redis_cache.RedisCacheBackend`
 * `app.core.helpers.cache.backends.inmemory_cache.InMemoryCacheBackend`
  
Also, you can customize and use your own one.
Customized backend is supposed to be based on [BaseCacheBackend class](/app/core/helpers/cache/backends/base_cache.py).

To set up custom backend you maybe need to add optional variables to .env. For example for RedisCacheBackend we use:
```
REDIS_HOSTNAME=xxxxxx.redis.cache.windows.net
REDIS_PASSWORD=<redis-key>
REDIS_DATABASE=13
REDIS_SSL=True
REDIS_PORT=6380
```

By default `ttl = 60` sec is used. It is possible to set another ttl through the `CACHE_DEFAULT_TTL` variable.
Also, it is possible to set ttl manually for a specific request directly at the place where @cache is used.

### Run with Docker

Docker-compose it is meant to be used for local development/testing, not for production, be aware that docker-compose uses higher privileges for development and testing purposes, we wouldn't recommend to use the [docker-compose](./docker-compose.yml) file for production, only for developers to be able to add changes and test them in local as well as unit/integration tests to avoid having to install all the dependencies.

#### Docker Flavor Versions (docker-compose)

* [app - Dockerfile](./Dockerfile) it is the default image to run in [docker-compose](./docker-compose.yml), it is a balanced docker production ready dockerfile which can be used to deploy application as well as to develop in your local.
* [tests - Dockerfile_test](./Dockerfile_test) Dockerfile definition which contains and install all dependencies needed for unit/integration tests.
* [Distroless - Dockerfile.distroless](./Dockerfile.distroless) Lean docker file (best approach for production systems due lack of unneeded binaries and libraries), this approach will be ideal to address security cve's and to have lean version of rafs-ddms.
  * Distroless build around ~400MB, you can test it `docker-compose --profile distroless up distroless`

#### Run App

**WARN** Docker-compose it is meant to be used for local development/testing, not for production.

```shell
if [ -z $UID ]; then export UID=$(id -u); fi
export GID=$(id -g)
docker-compose up app
```

#### Run with Dockerfile
```
export BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
export COMMIT_ID=$(git rev-parse HEAD)
export COMMIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
export COMMIT_MESSAGE=$(git log -1 --pretty=%B)

docker build -f "./Dockerfile" \
    --build-arg build_date="$BUILD_DATE" \
    --build-arg commit_id="$COMMIT_ID" \
    --build-arg commit_branch="$COMMIT_BRANCH" \
    --build-arg commit_message="$COMMIT_MESSAGE" . \
    -t rafs-ddms:latest

docker run rafs-ddms:latest
```

### Run with Uvicorn

```
uvicorn app.main:app --port LOCAL_PORT
```

To see the OpenAPI page, follow the link:

`http://127.0.0.1:<LOCAL_PORT>/<OPENAPI_PREFIX>/docs`

Use the `OPENAPI_PREFIX` value used for project settings.

## Testing

### Run Tests

**WARN** Docker-compose it is meant to be used for local development/testing, not for production.

Unit tests

```shell
docker-compose run tests
```

### Run Integration Tests

Using Docker [env substitution from shell](https://docs.docker.com/compose/environment-variables/set-environment-variables/#substitute-from-the-shell) capabilities.

```shell
# Export needed envs for testing
# Internal hostname in docker-compose (app)
# Alternatively you can choose to test in remote env
export DDMS_BASE_URL=http://app:8080  # Alternatively for distroless profile http://distroless:8088
export ACCESS_TOKEN=<access_token>
# Run test
docker-compose --profile integration run integration

# (Optional) Cleanup
docker-compose down
```

### Run Postman Tests

[The following collection](https://community.opengroup.org/osdu/platform/testing) can be used to test RAFS DDMS with Postman.

## Contribution

### Manage package dependencies

If new dependencies were added a new `requirements.txt` file must be generated by:

1. Add new dependencies to requirements.in
2. Run to generate a new requirements.txt file

```shell
pip install pip-tools 
pip-compile requirements.in
```

### Manage package dependencies - Tests

Testing dependencies are separated from the production dependencies.

1. Add new dependencies to `requirements-tests.in`
2. Run to generate a new requirements.txt file

```shell
pip install pip-tools 
pip-compile requirements.in requirements-tests.in -o requirements-tests.txt -v
pip install -r requirements-tests.txt
```

### Code Style Check
There is a list of linters and formatters which are used in this project for code style check.
Mostly it is [flake8](https://flake8.pycqa.org/en/latest/)
with [wemake-python-styleguide extension](https://wemake-python-styleguide.readthedocs.io/en/latest/index.html).

Full list of checkers can be found in [pre-commit config](.pre-commit-config.yaml) file. Configuration for
checkers is in [setup.cfg](setup.cfg) file.

#### Pre-commit Hooks Installation

Pre-commit hooks are supposed to be installed locally.

All requirements for development, tests and pre-commit checks can be installed to your python environment:

```shell
pip-compile requirements.in requirements-tests.in -o requirements-tests.txt -v
pip install -r requirements-tests.txt
```

pre-commit tool should be used inside this environment.

Steps after requirements installation:

```shell
pre-commit install
pre-commit install --hook-type commit-msg
```
Second step is needed for correct gitlint work.

#### Pre-commit Hooks Run
Command to run pre-commit manually for all files:

```shell
pre-commit run --all-files
```

In other cases, all checks run automatically on commit.

## Deployment

* [Main deployment page](./devops/)

### Azure

* [Azure Deployment Instructions - Standard DDMS](./devops/azure/)

## License
Licensed under Apache License Version 2.0; details can be found in [LICENSE](./LICENSE). 
