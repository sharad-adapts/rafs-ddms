## OSDU Models
The osdu models are pydantic version of OSDU Json schema models.

### How to generate them
1. Install pydantic code generator
```
pip install datamodel-code-generator
```
2. Prepare url, partition_id, schema_id and token
```
export SCHEMA_BASE_URL="${OSDU_BASE_URL}/api/schema-service/v1/schema"
export SCHEMA_ID="osdu:wks:master-data--Coring:1.0.0"
export TOKEN="..."
export PARTITION_ID="opendes"
```
3. Issue the command
```
datamodel-codegen \
  --url "$SCHEMA_BASE_URL/$SCHEMA_ID" \
  --http-headers "Authorization: Bearer $TOKEN" "data-partition-id: $PARTITION_ID" "Content-Type: application/json" \
  --input-file-type jsonschema \
  --output app/models/domain/osdu/ \
  --reuse-model
```
4. The model is created in osdu folder under the `\_\_init\_\_.py` module
5. Manually do the following fixes:
    - Make sure all imports of init file are correct (some times a dot is missing in a few imports)
    - Rename the `\_\_init\_\_.py` module to the name of the type + the version, i.e., MDCoring100, WPCRockSampleAnalysis110, etc.
    - Add it to IMPLEMENTED_MODELS map in the `base.py` module.

*NOTE:* Within [AbstractCommonResources](app/models/domain/osdu/osdu_wks_AbstractCommonResources_1/field_0.py) there are fields 
(`ResourceHomeRegionID`, `ResourceHostRegionIDs`, `ResourceSecurityClassification`) that contain a manually added field  
`copy_to_dataset_record`. This addition is for the purpose of inheritance.
