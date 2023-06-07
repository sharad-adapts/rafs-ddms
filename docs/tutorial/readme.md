# RAFS DDMS Tutorial

## Getting started
This prototype supports the following endpoints
- [GET/POST] RockSampleAnalysis metadata
- [GET/POST] Routine Core Analysis bulk data (either in parquet or json)

#### Pre-requisites
- [Optional] Coring, RockSample and Wellbore master data should be already ingested
- [Required] Have ready acl, legal and all required info for RockSampleAnalysis metadata ingestion
- [Required] Have access and permissions to the data partition 


#### API
Get familiar with api documentation in [REST docs](../spec/openapi.json)

#### Post and Get RockSampleAnalysis WPC metadata.
1. Prepare json file to comply with ```osdu:work-product-component--RockSampleAnalysis:1.1.0``` schema.
2. Issue following POST request:
```
curl --location --request POST '{RAFS_DDMS_URL}/api/os-rafs-ddms/rocksampleanalyses/' \
--header 'Content-Type: application/json' \
--header 'data-partition-id: opendes' \
--header 'Authorization: Bearer token' \
--data-raw '{
    "id": "opendes:work-product-component--RockSampleAnalysis:Test_Example",
    ...
   }'
```
Response should be an id with its corresponding version, i.e.,  ```opendes:work-product-component--RockSampleAnalysis:Test_Example:1673921980922175```

3. Get the record with following GET request:
```
curl --location --request GET '{RAFS_DDMS_URL}/api/os-rafs-ddms/rocksampleanalyses/opendes:work-product-component--RockSampleAnalysis:Test_Example' \
--header 'Content-Type: application/json' \
--header 'data-partition-id: opendes' \
--header 'Authorization: Bearer token'
```
4. Alternatively, get the all versions of a record and fetch the specific version with following endpoints, respectively:
```
{RAFS_DDMS_URL}/api/os-rafs-ddms/rocksampleanalyses/opendes:work-product-component--RockSampleAnalysis:Test_Example/versions
{RAFS_DDMS_URL}/api/os-rafs-ddms/rocksampleanalyses/opendes:work-product-component--RockSampleAnalysis:Test_Example/versions/{VERSION_NUMBER}
```

#### Post and Get Routine Core Analysis bulk data.
1. Endpoint accepts either a json pandas dataframe with orient = "split" or a parquet file just by adjusting the content-type header to one of the following options
```
Content-Type: application/json
Content-Type: x-parquet
```
2. Example request with json payload (endpoint loads it and converts it to parquet to save it as dataset):
```
curl --location --request POST '{RAFS_DDMS_URL}/api/os-rafs-ddms/rocksampleanalyses/opendes:work-product-component--RockSampleAnalysis:Test_Example/rca/data' \
--header 'data-partition-id: opendes' \
--header 'Authorization: Bearer token' \
--header 'Content-Type: application/json' \
--data-raw '{
  "columns": [
    "Country",
    "Field",
    "Wellbore",
    "Depth",
    "Type",
    "Number",
    "Laboratory",
    "Report",
    "Grain-density",
    "Porosity",
    "Saturation-oil",
    "Lithology",
    "Comments"
  ],
  "index": [
    1,
  ],
  "data": [
    [
      "Norway",
      "VOLVE",
      "NO 15\/9-19 A",
      3837.0,
      "Plug_RCA",
      1.0,
      "Unknown",
      "Merge from EPDS RCA",
      2.66,
      "0.1697",
      null,
      "Sst.lt-Brn.M-gr.Ang.W-cmt.Fr-srt.mtrx.frac.w\/Mic,Pyr,Calc,C,",
      "RCA data transfer from EPDS"
    ]
  ]
}'
```
3. Example with parquet payload:
```
curl --location --request POST '{RAFS_DDMS_URL}/api/os-rafs-ddms/rocksampleanalyses/opendes:work-product-component--RockSampleAnalysis:Test_Example/rca/data' \
--header 'data-partition-id: opendes' \
--header 'Content-Type: application/x-parquet' \
--header 'Authorization: Bearer token' \
--data-binary '@/Path/to/parquet/file.parquet'
```
In both cases the id of the dataset created with the parquet data is returned and the RockSampleAnalysis WPC datasets are updated with it:
```
{
    "id": "opendes:dataset--File.Generic:routine-core-analysis-61202228-4ca8-406b-ac4f-a9153dac56d6"
}
```
Datasets field of ```opendes:work-product-component--RockSampleAnalysis:Test_Example``` is updated
```
"Datasets": [
    "opendes:dataset--File.Generic:WellCompletionReport-KentishKnockSouth1-WA-365-P--R1:",
    "opendes:dataset--File.Generic:routine-core-analysis-61202228-4ca8-406b-ac4f-a9153dac56d6:"
],
```
4. Data can be retrieved also in json or parquet formats and optionally filters at row and column level can be applied.
5. Example get raw parquet data:
```
curl --location --request GET '{RAFS_DDMS_URL}/api/os-rafs-ddms/rocksampleanalyses/opendes:work-product-component--RockSampleAnalysis:Test_Example/rca/data' \
--header 'data-partition-id: opendes' \
--header 'Content-Type: application/x-parquet' \
--header 'Authorization: Bearer token'
```
6. Example get data as json pandas dataframe with filters.
```
curl --location --request GET '{RAFS_DDMS_URL}/api/os-rafs-ddms/rocksampleanalyses/opendes:work-product-component--RockSampleAnalysis:Test_Example/rca/data?columns_filter=Depth,Porosity&rows_filter=Depth,gt,3850' \
--header 'data-partition-id: opendes' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer token'
```
Columns filter is a comma separated list of projected column names ```ColumnName1,ColumnName2```

Rows filter is a comma separated list that represent a condition (current implementation only allows a single condition) with the following format ```ColumnName,Operator,Value```

Valid operators are strings and their math operator equivalent is decribed in following dictionary:
```
 {"lt": "<", "gt": ">", "lte": "<=", "gte": ">=", "eq": "=", "neq": "!="}
```
Response will only contain the project columns that comply with the row condition filter.

7. Example with aggregation over a column (current implementation allows only one column aggregation)
```
curl --location --request GET '{RAFS_DDMS_URL}/api/os-rafs-ddms/rocksampleanalyses/opendes:work-product-component--RockSampleAnalysis:Test_Example/rca/data?columns_filter=Porosity&columns_aggregation=Porosity,avg' \
--header 'data-partition-id: opendes' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer token'
```
Apply the column filter over the column you want to do the aggregation and then add the aggregation as ```ColumnName,aggregation```

Supported aggregations depends on column type but in general:
```
[avg, count, max, min, sum]
```
8. Column aggregation and row filtering support ```ColumnName.FieldName``` syntax to work over nested fields.

For example todo a row filtering and aggregation over a column named ```Permeability``` which has the following object as value
```
{
  Value: 1000.0,
  UnitOfMeasure: "osdu:reference-data--UnitOfMeasure:mD
}
```
The rows_filter parameter would be
```
rows_filter=Permeability.Value,lt,1000
```

And the colums_aggregation parameter would be:
```
columns_aggregation=Permeability.Value,avg
```
