# RAFS Metrics and monitoring

Grafana and prometheus are tools which are popular for metrics monitoring, you can use managed solution, even grafana cloud to be able to see your scraped metrics from prometheus, in this section we will cover only [Grafana Azure](#azure-grafana) along with local setup, you can load the grafana dashboards in your preferred managed or self-managed grafana instance.

For the resource metrics, each CSP has their own solution to check container consumption and metrics, also prometheus fast-api, however, those are cpu time and memory bytes consumed, not showing really the percentaje of cpu's and memory which will be used inside the cluster/node.

## Local docker-compose metrics

```shell
# Start monitoring services
docker-compose up

# In another terminal to generate some metrics.
export ACCESS_TOKEN="..."
docker-compose --profile integration run integration
```

Check browser in [localhost:3000](http://localhost:3000/) for grafana access.

### Infrastructure related metrics

To check the pod consumption, we can use `kubectl top pod -n ddms-rafs`, each cloud provider has their own metrics implementation to check pod consumption and so on.

## Azure

Container insights can be used to check container CPU Usage and advanced monitoring features, in community version go to `RG > ContainerInsights < Log Analytics Workspace`.

More info about this:

* [Container CPU](https://learn.microsoft.com/en-us/azure/azure-monitor/containers/container-insights-log-query#container-cpu)
* [Container Memory](https://learn.microsoft.com/en-us/azure/azure-monitor/containers/container-insights-log-query#container-memory)

### Azure Grafana

1. You need to enable the prometheus metrics in azure portal or with azure cli. [docs](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/prometheus-metrics-enable?tabs=cli)
2. Create managed grafana for metrics visualization [docs](https://learn.microsoft.com/en-us/azure/managed-grafana/quickstart-managed-grafana-portal).
3. [Send Data to Azure monitorn managed service for prometheus](https://learn.microsoft.com/en-us/azure/azure-monitor/containers/container-insights-prometheus?tabs=cluster-wide#send-data-to-azure-monitor-managed-service-for-prometheus)
