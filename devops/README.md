# RAFSDDMS production deployment

## [Cloud Agnostic] Build image

**WARNING:** It is recommended to use the [Dockerfile](../../Dockerfile) image for production systems.  The [Dockerfile.tests](../../Dockerfile.tests) image, contains extra dependencies needed for testing purposes and is not intended for production use.

```shell
docker build --file ./Dockerfile -t rafsddms:latest .
```

## Cloud specific

### Azure

* [Azure deployment instructions](./azure/)
* [Azure monitoring local setup](./azure/monitoring/)

## Register service

Register service it is used for ddms visibility, in rafs-ddms mvp1 CICD will register the latest specs in each register service environment. More documentation on how to implement this in [register docs](../docs/register/).
