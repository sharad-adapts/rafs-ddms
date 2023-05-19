# RAFSDDMS production deployment

## [Cloud Agnostic] Build image

**WARN** It is recommended to use the [distroless](../../Dockerfile.distroless) image for production systems, which it is more secure and lighter than develop and test images.

```shell
docker build --file ./Dockerfile.distroless -t rafsddms:latest .
```

## Cloud specific

### Azure

* [Azure deployment instructions](./azure/)
* [Azure monitoring local setup](./azure/monitoring/)

## Register service

Register service it is used for ddms visibility, in rafs-ddms mvp1 CICD will register the latest specs in each register service environment. More documentation on how to implement this in [register docs](../docs/register/).
