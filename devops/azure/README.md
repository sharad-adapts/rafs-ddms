# RAFSDDMS on Azure

## Build image

**WARN** It is recommended to use the [distroless](../../Dockerfile) image for production systems, which it is more secure and lighter than develop and test images.

```shell
az login
az acr build --registry <acr-name> --file ./Dockerfile -t rafsddms:latest .
```

## Community installation

Using [helm-charts-azure/standard-ddms](https://community.opengroup.org/osdu/platform/deployment-and-operations/helm-charts-azure/-/tree/master/osdu-ddms/standard-ddms) for simplicity.

### AKS Install Process

#### Chart Parameters

There are instance specific parameters within Helm chart:

| Parameter             | Description                                           |
| --------------------- | ----------------------------------------------------- |
| <azure_tenant>        | Azure Tenant of Compute RG                            |
| <azure_subscription>  | Azure Subscription of Compute RG                      |
| <azure_resourcegroup> | Name of Compute RG                                    |
| <azure_identity>      | Name of MSI that is used by Pods in AKS               |
| <azure_identity_id>   | ID of MSI                                             |
| <azure_keyvault>      | Name of KeyVault in Compute RG with platform secrets  |
| <azure_appid>         | ...                                                   |
| <azure_acr>           | Name of Azure Container Registry with Images to use   |
| <ingress_dns>         | DNS name associated with the Instance                 |

Following instruction show general process of using Standard Helm for deployment of particular services.

```bash
UNIQUE=<uniquename> # I.E glab

ingress_dns='...' # kubectl get ingress -n osdu-azure / kubectl get virtualservice -n istio-system
azure_acr='<acr.domain.name>' # The acr name I.E osdumvpcr{{company}}ajlhcr.azurecr.io
GROUP=$(az group list --query "[?contains(name, 'cr${UNIQUE}')].name" -otsv)
ENV_VAULT=$(az keyvault list --resource-group $GROUP --query [].name -otsv)

azure_tenant=$(az keyvault secret show --id https://${ENV_VAULT}.vault.azure.net/secrets/tenant-id --query value -otsv)
azure_subscription=$(az keyvault secret show --id https://${ENV_VAULT}.vault.azure.net/secrets/subscription-id --query value -otsv)
azure_resourcegroup=$(az keyvault secret show --id https://${ENV_VAULT}.vault.azure.net/secrets/base-name-cr --query value -otsv)-rg
azure_identity=$(az keyvault secret show --id https://${ENV_VAULT}.vault.azure.net/secrets/base-name-cr --query value -otsv)-osdu-identity
azure_identity_id=$(az keyvault secret show --id https://${ENV_VAULT}.vault.azure.net/secrets/osdu-identity-id --query value -otsv)

ddms='rafs'
namespace='ddms-rafs'
azure_keyvault=$ENV_VAULT

# Make sure you are on the correct subscription and connected to the right AKS.
az account set --subscription $azure_subscription
az aks get-credentials --resource-group $azure_resourcegroup --name <azure_kubernetese_service>
```

Rafdms has its own values file, dry run template

```bash
helm template "oci://msosdu.azurecr.io/helm/standard-ddms" --version 1.18.0-r -f devops/azure/values.yaml
```

Install the helm chart.

```bash
# Create K8S Namespace with configured Istio sidecar ingejction
kubectl create namespace $namespace && \
kubectl label namespace $namespace istio-injection=enabled

# Example of deployment for Wellbore DDMS
helm upgrade -i ${ddms}-services "oci://msosdu.azurecr.io/helm/standard-ddms" --version 1.18.0-r -n $namespace \
  -f devops/azure/values.yaml \
  --set azure.tenant=$azure_tenant \
  --set azure.subscription=$azure_subscription \
  --set azure.resourcegroup=$azure_resourcegroup \
  --set azure.identity=$azure_identity \
  --set azure.identity_id=$azure_identity_id \
  --set azure.keyvault.name=$azure_keyvault \
  --set azure.acr=$azure_acr \
  --set ingress.dns=$ingress_dns \
  --set configuration[0].container.image=rafsddms \
  --set configuration[0].container.tag=latest --debug
```
