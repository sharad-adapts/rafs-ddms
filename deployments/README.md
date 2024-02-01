## OSDU Well Known Schemas Disclaimer

Note regarding OSDU Well Known Schema interaction: Currently (January 2024), OSDU Data Definitions "Fluid Samples" and "Samples & Petrophysics" Project teams re-worked the data model for both rock and fluid samples in a way that there is a unified way to handle both.

Important Schemas to refer when using RAFSDDMS:

- [osdu:wks:master-data--GenericFacility:1.0.0](https://community.opengroup.org/osdu/platform/system/schema-service/-/blob/master/deployments/shared-schemas/osdu/master-data/GenericFacility.1.0.0.json?ref_type=heads)
- [osdu:wks:master-data--GenericSite:1.0.0](https://community.opengroup.org/osdu/platform/system/schema-service/-/blob/master/deployments/shared-schemas/osdu/master-data/GenericSite.1.0.0.json?ref_type=heads)
- [osdu:wks:master-data--Sample:2.0.0](https://community.opengroup.org/osdu/platform/system/schema-service/-/blob/master/deployments/shared-schemas/osdu/master-data/Sample.2.0.0.json?ref_type=heads)
- [osdu:wks:master-data--SampleAcquisitionJob:1.0.0](https://community.opengroup.org/osdu/platform/system/schema-service/-/blob/master/deployments/shared-schemas/osdu/master-data/SampleAcquisitionJob.1.0.0.json?ref_type=heads) 
- [osdu:wks:master-data--SampleChainOfCustodyEvent:1.0.0](https://community.opengroup.org/osdu/platform/system/schema-service/-/blob/master/deployments/shared-schemas/osdu/master-data/SampleChainOfCustodyEvent.1.0.0.json?ref_type=heads)
- [osdu:wks:master-data--SampleContainer:1.0.0](https://community.opengroup.org/osdu/platform/system/schema-service/-/blob/master/deployments/shared-schemas/osdu/master-data/SampleAcquisitionJob.1.0.0.json?ref_type=heads)
- [osdu:wks:work-product-component--SamplesAnalysesReport:1.0.0](https://community.opengroup.org/osdu/platform/system/schema-service/-/blob/master/deployments/shared-schemas/osdu/work-product-component/SamplesAnalysesReport.1.0.0.json?ref_type=heads)
- [osdu:wks:work-product-component--SamplesAnalysis:1.0.0](https://community.opengroup.org/osdu/platform/system/schema-service/-/blob/master/deployments/shared-schemas/osdu/work-product-component/SamplesAnalysis.1.0.0.json?ref_type=heads)

### Legacy schemas that will be removed once Api V1 is fully removed.
All [rafsddms WorkProductComponent schemas](./shared-schemas/rafsddms/work-product-component/) will be removed.

## Custom RAFS DDMS Schemas Usage

As of Jan 2024, the RAFS DDMS [content schemas](https://community.opengroup.org/osdu/platform/domain-data-mgmt-services/rock-and-fluid-sample/rafs-ddms-services/-/tree/main/app/models/data_schemas) may use reference data that is still not published in the OSDU forum, for both: schema definition and values.

### Schemas Registration

Before registering the schemas the next variables must be populated:

`{{rafsddms-schema-authority}}` - the custom schemas will have their own schema authority.

`{{schema-authority}}` - the schema authority that was used for the OSDU WKS schemas.

`{{SCHEMA_HOST}}` - the schema service, example: {{HOSTNAME}}/api/schema-service/v1.

We provide the schema definition for such reference data in the [reference-data](./shared-schemas/rafsddms/reference-data/) folder. The [Schemas Postman Collection](./rafsddms_schemas_mvp.postman_collection.json) can be used for the schemas registration.

### Reference Data Values Upload

Before uploading reference-data values the following variables must be populated ont the collection:

`WORKFLOW_URL` - the workflow url, example: {{HOSTNAME}}/api/workflow/v1

`NAMESPACE` - the data partition id
 
 `DATA_OWNERS_GROUP` and `DATA_VIEWERS_GROUP` for acl part of record

 `DATA_VIEWERS_GROUP` and `ISO_3166_ALPHA_2_CODE` for legal of record

The list of values can be found in [The Reference Values Postman Collection](./rafsddms_ref_data_manifests_mvp.postman_collection.json) and can be used to upload the reference-data values.

#### OSDU Reference Data
New reference-data has been added to OSDU since M21 and it's of particular relevance for the RAFS-DDMS, since it's utilized in the content schemas.

Schemas can be found for each type:
 - [SampleAnalysisFamily](https://community.opengroup.org/osdu/platform/system/schema-service/-/blob/master/deployments/shared-schemas/osdu/reference-data/SampleAnalysisFamily.1.0.0.json?ref_type=heads)
 - [SampleAnalysisSubFamily](https://community.opengroup.org/osdu/platform/system/schema-service/-/blob/master/deployments/shared-schemas/osdu/reference-data/SampleAnalysisSubFamily.1.0.0.json?ref_type=heads)
 - [SampleAnalysisType](https://community.opengroup.org/osdu/platform/system/schema-service/-/blob/master/deployments/shared-schemas/osdu/reference-data/SampleAnalysisType.1.0.0.json?ref_type=heads)
 - [SamplesAnalysisCategoryTag](https://community.opengroup.org/osdu/platform/system/schema-service/-/blob/master/deployments/shared-schemas/osdu/reference-data/SamplesAnalysisCategoryTag.1.0.0.json?ref_type=heads)

 And its corresponding reference values:
 - [SampleAnalysisFamily](https://community.opengroup.org/osdu/data/data-definitions/-/blob/master/ReferenceValues/Manifests/reference-data/OPEN/SampleAnalysisFamily.1.0.0.json?ref_type=heads)
 - [SampleAnalysisSubFamily](https://community.opengroup.org/osdu/data/data-definitions/-/blob/master/ReferenceValues/Manifests/reference-data/OPEN/SampleAnalysisSubFamily.1.0.0.json?ref_type=heads)
 - [SampleAnalysisType](https://community.opengroup.org/osdu/data/data-definitions/-/blob/master/ReferenceValues/Manifests/reference-data/OPEN/SampleAnalysisType.1.0.0.json?ref_type=heads)
 - [SamplesAnalysisCategoryTag](https://community.opengroup.org/osdu/data/data-definitions/-/blob/master/ReferenceValues/Manifests/reference-data/LOCAL/SamplesAnalysisCategoryTag.1.0.0.json?ref_type=heads)
