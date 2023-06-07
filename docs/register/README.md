# RAFS-DDMS Integration with register service

- [RAFS-DDMS Integration with register service](#rafs-ddms-integration-with-register-service)
  - [Pre Requisites ](#pre-requisites-)
  - [Register as a DDMS ](#register-as-a-ddms-)
  - [Client discover ddms type ](#client-discover-ddms-type-)
  - [Client retrieves Single Entity id data ](#client-retrieves-single-entity-id-data-)

The following directions are from [register service](https://community.opengroup.org/osdu/platform/system/register/-/blob/master/docs/tutorial/HowToBecomeADDMS.md) in community.

## Pre Requisites <a name="prerequisites"></a>

* [Optional] Coring, RockSample and Wellbore master data should be already ingested
  * Schemas for [RockSample](https://community.opengroup.org/osdu/platform/system/schema-service/-/tree/master/deployments/shared-schemas/osdu), [RockAnalysis](https://community.opengroup.org/osdu/platform/system/schema-service/-/tree/master/deployments/shared-schemas/osdu), and [Coring](https://community.opengroup.org/osdu/platform/system/schema-service/-/tree/master/deployments/shared-schemas/osdu) should be already uploaded.
* [Required] Have ready acl, legal and all required info for RockSampleAnalysis metadata ingestion
* [Required] Have access and permissions to the data partition.
* [Required for Single Entity retrieve] Need to use register service version `> M17 (release/0.20)`, there is a [bug](https://community.opengroup.org/osdu/platform/system/register/-/issues/40) which not allows recent ddms's behavior.

## Register as a DDMS <a name="register"></a>

The first step is to register as a DDMS. This makes your DDMS discoverable to clients and presents them with an API definition that tells them how to retrieve the bulk data when a record from their DDMS is discovered.

For sake of convenience we are updating the [rafsddms_register.json](rafsddms_register.json), which is supposed to contains the latest payload of the openapispec for register service interaction.  **NOTE:** Update your URls, replacing `{{company}}`

```shell
sed -i 
curl -k -XPOST --header "Authorization: Bearer ${ACCESS_TOKEN}" \
  --header 'Content-Type: application/json' --header 'data-partition-id: opendes' \
  https://${AZURE_DNS_NAME}/api/register/v1/ddms --data-binary "@rafsddms_register.json"
```

## Client discover ddms type <a name="discover-rafs"></a>

It can be either `rocksampleanalysis|coring|rocksample` for type discovery.

```shell
{{osdu_endpoint}}/api/register/v1/ddms?type=rocksampleanalysis
{{osdu_endpoint}}/api/register/v1/ddms/rafs
```

## Client retrieves Single Entity id data <a name="retrieve-single-id"></a>

Client should have already some data/record id for the ddms, I.E. `opendes:master-data--Wellbore:NPD-3180`.

You can retrieve them directly with register service Single Entity retrieval.

<details><summary>curl</summary>

```text
    curl --request GET \
    --url '/api/register/v1/ddms/rafs/rocksampleanalyses/opendes:work-product-component--RockSampleAnalysis:Test_Example' \
    --header 'authorization: Bearer <JWT>' \
    --header 'content-type: application/json' \
    --header 'data-partition-id: opendes' 
```

</details>

This will redirect `307` to the proper DDMS url

<details><summary>verbose curl response</summary>

```text
x-frame-options: DENY
strict-transport-security: max-age=31536000; includeSubDomains
cache-control: no-cache, no-store, must-revalidate
access-control-allow-origin: *
access-control-allow-credentials: true
access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH
x-content-type-options: nosniff
content-security-policy: default-src 'self'
expires: 0
x-xss-protection: 1; mode=block
access-control-max-age: 3600
access-control-allow-headers: access-control-allow-origin, origin, content-type, accept, authorization, data-partition-id, correlation-id, appkey
correlation-id: 2158bdd8-d098-44d4-9b78-33410b967979
location: //https://<osdu-instance-fqdn>/api/rafs-ddms/v1/rocksampleanalyses/opendes:work-product-component--RockSampleAnalysis:Test_Example
content-length: 0
date: Wed, 22 Feb 2023 00:07:30 GMT
x-envoy-upstream-service-time: 119
server: istio-envoy

HTTP/2 405 
date: Wed, 22 Feb 2023 00:07:29 GMT
server: istio-envoy
content-length: 33
content-type: application/json
x-envoy-upstream-service-time: 15

{
    "id": "opendes:work-product-component--RockSampleAnalysis:Test_Example",
    "version": 1677019773435718,
    "kind": "osdu:wks:work-product-component--RockSampleAnalysis:1.1.0",
    "acl": {
        "viewers": [
            "data.default.viewers@opendes.contoso.com"
        ],
        "owners": [
            "data.default.owners@opendes.contoso.com"
        ]
    },
    "legal": {
        "legaltags": [
            "opendes-rafs-ddms-legal"
        ],
        "otherRelevantDataCountries": [
            "US"
        ],
        "status": "compliant"
    },
    "data": {
        "ActivityTemplateID": "opendes:master-data--ActivityTemplate:RoutineCoreAnalysis-0001:",
        "AnalysisDate": "2012-12-29",
        "AnalysisTypeIDs": [
            "opendes:reference-data--RockSampleAnalysisType:RoutineCoreAnalysis:"
        ],
        "Artefacts": [],
        "AuthorIDs": [
            "James Brown, Core Laboratories"
        ],
        "BottomDepth": 2423.26,
        "BusinessActivities": [
            "Rock Sample Analysis"
        ],
        "CoringID": "opendes:master-data--Coring:KKS1-Core-1:",
        "CreationDateTime": "2020-02-13T09:13:15.55Z",
        "Datasets": [
            "opendes:dataset--File.Generic:WellCompletionReport-KentishKnockSouth1-WA-365-P--R1:",
            "opendes:dataset--File.Generic:routine-core-analysis-61202228-4ca8-406b-ac4f-a9153dac56d6:"
        ],
        "DepthShiftsID": "opendes:work-product-component--WellLog:WellLog-911bb71f-06ab-4deb-8e68-b8c9229dc76b:",
        "Description": "Example Description",
        "ExtensionProperties": {},
        "GeoContexts": [
            {
                "GeoPoliticalEntityID": "opendes:master-data--GeoPoliticalEntity:3298:",
                "GeoTypeID": "opendes:reference-data--GeoPoliticalEntityType:BlockID:"
            },
            {
                "BasinID": "opendes:master-data--Basin:Carnarvon:",
                "GeoTypeID": "opendes:reference-data--BasinType:PassiveMargin:"
            },
            {
                "BasinID": "opendes:master-data--Field:Gorgon:",
                "GeoTypeID": "Field"
            }
        ],
        "IsDiscoverable": true,
        "IsExtendedLoad": true,
        "LineageAssertions": [
            {
                "ID": "opendes:work-product-component--Document:WellCompletionReport-KentishKnockSouth1-WA-365-P--R1:",
                "LineageRelationshipType": "opendes:reference-data--LineageRelationshipType:Direct:"
            }
        ],
        "Name": "10A",
        "Parameters": [
            {
                "Index": 0,
                "ParameterKindID": "opendes:reference-data--ParameterKind:String:",
                "ParameterRoleID": "opendes:reference-data--ParameterRole:Input:",
                "StringParameter": "Hot solvent: tetrahydrofuran, toluene & methanol",
                "Title": "SampleCleaning"
            },
            {
                "Index": 0,
                "ParameterKindID": "opendes:reference-data--ParameterKind:String:",
                "ParameterRoleID": "opendes:reference-data--ParameterRole:Input:",
                "StringParameter": "Convection oven @ 105 degC",
                "Title": "SampleDrying"
            },
            {
                "Index": 0,
                "ParameterKindID": "opendes:reference-data--ParameterKind:String:",
                "ParameterRoleID": "opendes:reference-data--ParameterRole:Input:",
                "StringParameter": "Horizontal samples (Suffix A) plugs were drilled and trimmed using chilled Nitrogen gas every 0.30m for routine core analysis (most of the samples were sleeved in nickel with steel screens). The horizontal plugs were cleaned of residual hydrocarbons and salts using warm THF, warm toluene and warm methanol respectively. Hydrocarbon removal was confirmed by gas chromatography analysis of the toluene, while salt removal was indicated by a negative reaction to silver nitrate in the methanol. After cleaning, the samples were dried in a convection oven at 105°C to a constant weight +/- 0.02 g. After drying, the samples were cooled down to room temperature in a desiccator, prior to analysis.",
                "Title": "SamplePreparationDescription"
            }
        ],
        "Remarks": [
            {
                "Remark": "Mounted",
                "RemarkID": "Remark 1",
                "RemarkSource": "Kentish Knock South 1 Completion Report, page 453."
            }
        ],
        "RockSampleID": "opendes:master-data--RockSample:KKS1-Core1-Sample-10A:",
        "RoutineCoreAnalysis": {
            "GrainDensity": 2.643,
            "GrainDensityMeasurementTypeID": "opendes:reference-data--GrainDensityMeasurementType:BoylesLaw:",
            "RCAMeasurements": [
                {
                    "Conditions": {
                        "OtherConditions": [],
                        "Pressure": 800,
                        "PressureMeasurementTypeID": "opendes:reference-data--PressureMeasurementType:Overburden:",
                        "Temperature": 12345.6
                    },
                    "OtherMeasurements": [],
                    "Permeability": 4410.0,
                    "PermeabilityMeasurementTypeID": "opendes:reference-data--PermeabilityMeasurementType:Gas:",
                    "Porosity": 35.7,
                    "PorosityMeasurementTypeID": "opendes:reference-data--PorosityMeasurementType:HeliumInjection:"
                },
                {
                    "Conditions": {
                        "OtherConditions": [],
                        "Pressure": 1280,
                        "PressureMeasurementTypeID": "opendes:reference-data--PressureMeasurementType:Overburden:"
                    },
                    "OtherMeasurements": [],
                    "Permeability": 4340.0,
                    "PermeabilityMeasurementTypeID": "opendes:reference-data--PermeabilityMeasurementType:Gas:",
                    "Porosity": 35.4,
                    "PorosityMeasurementTypeID": "opendes:reference-data--PorosityMeasurementType:HeliumInjection:"
                }
            ]
        },
        "SampleOrientationID": "opendes:reference-data--SampleOrientationType:Horizontal:",
        "SpatialPoint": {
            "AppliedOperations": [
                "conversion from GDA_1994_MGA_Zone_49 to GCS_GDA_1994; 1 points converted",
                "transformation GCS_GDA_1994 to GCS_WGS_1984 using GDA_1994_To_WGS_1984; 1 points successfully transformed"
            ],
            "AsIngestedCoordinates": {
                "CoordinateReferenceSystemID": "opendes:reference-data--CoordinateReferenceSystem:BoundProjected:EPSG::28349_EPSG::1150:",
                "features": [
                    {
                        "geometry": {
                            "coordinates": [
                                689960.85,
                                7811747.53
                            ],
                            "type": "AnyCrsPoint"
                        },
                        "properties": {},
                        "type": "AnyCrsFeature"
                    }
                ],
                "persistableReferenceCrs": "{\"authCode\":{\"auth\":\"OSDU\",\"code\":\"28349001\"},\"lateBoundCRS\":{\"authCode\":{\"auth\":\"EPSG\",\"code\":\"28349\"},\"name\":\"GDA_1994_MGA_Zone_49\",\"type\":\"LBC\",\"ver\":\"PE_10_9_1\",\"wkt\":\"PROJCS[\\\"GDA_1994_MGA_Zone_49\\\",GEOGCS[\\\"GCS_GDA_1994\\\",DATUM[\\\"D_GDA_1994\\\",SPHEROID[\\\"GRS_1980\\\",6378137.0,298.257222101]],PRIMEM[\\\"Greenwich\\\",0.0],UNIT[\\\"Degree\\\",0.0174532925199433]],PROJECTION[\\\"Transverse_Mercator\\\"],PARAMETER[\\\"False_Easting\\\",500000.0],PARAMETER[\\\"False_Northing\\\",10000000.0],PARAMETER[\\\"Central_Meridian\\\",111.0],PARAMETER[\\\"Scale_Factor\\\",0.9996],PARAMETER[\\\"Latitude_Of_Origin\\\",0.0],UNIT[\\\"Meter\\\",1.0],AUTHORITY[\\\"EPSG\\\",28349]]\"},\"name\":\"GDA94 * EPSG-Aus / Map Grid of Australia zone 49 [28349,1150]\",\"singleCT\":{\"authCode\":{\"auth\":\"EPSG\",\"code\":\"1150\"},\"name\":\"GDA_1994_To_WGS_1984\",\"type\":\"ST\",\"ver\":\"PE_10_9_1\",\"wkt\":\"GEOGTRAN[\\\"GDA_1994_To_WGS_1984\\\",GEOGCS[\\\"GCS_GDA_1994\\\",DATUM[\\\"D_GDA_1994\\\",SPHEROID[\\\"GRS_1980\\\",6378137.0,298.257222101]],PRIMEM[\\\"Greenwich\\\",0.0],UNIT[\\\"Degree\\\",0.0174532925199433]],GEOGCS[\\\"GCS_WGS_1984\\\",DATUM[\\\"D_WGS_1984\\\",SPHEROID[\\\"WGS_1984\\\",6378137.0,298.257223563]],PRIMEM[\\\"Greenwich\\\",0.0],UNIT[\\\"Degree\\\",0.0174532925199433]],METHOD[\\\"Position_Vector\\\"],PARAMETER[\\\"X_Axis_Translation\\\",0.0],PARAMETER[\\\"Y_Axis_Translation\\\",0.0],PARAMETER[\\\"Z_Axis_Translation\\\",0.0],PARAMETER[\\\"X_Axis_Rotation\\\",0.0],PARAMETER[\\\"Y_Axis_Rotation\\\",0.0],PARAMETER[\\\"Z_Axis_Rotation\\\",0.0],PARAMETER[\\\"Scale_Difference\\\",0.0],OPERATIONACCURACY[3.2],AUTHORITY[\\\"EPSG\\\",1150]]\"},\"type\":\"EBC\",\"ver\":\"PE_10_9_1\"}",
                "type": "AnyCrsFeatureCollection"
            },
            "Wgs84Coordinates": {
                "features": [
                    {
                        "geometry": {
                            "coordinates": [
                                112.81324757107716,
                                -19.7808907610266
                            ],
                            "type": "Point"
                        },
                        "properties": {},
                        "type": "Feature"
                    }
                ],
                "type": "FeatureCollection"
            }
        },
        "SubmitterName": "Core Laboratories Australia",
        "Tags": [
            "Example Tags"
        ],
        "TechnicalAssuranceID": "opendes:reference-data--TechnicalAssuranceType:Certified:",
        "TopDepth": 2423.26,
        "VerticalMeasurement": {
            "VerticalMeasurement": 0.0,
            "VerticalMeasurementDescription": "Same vertical reference as wellbore ZDP, Measured Depth, Drillers Depth.",
            "VerticalMeasurementPathID": "opendes:reference-data--VerticalMeasurementPath:MeasuredDepth:",
            "VerticalMeasurementSourceID": "opendes:reference-data--VerticalMeasurementSource:DRL:",
            "VerticalReferenceID": "ZDP"
        },
        "WellboreID": "opendes:master-data--Wellbore:KKS1:"
    },
    "ancestry": {
        "parents": []
    },
    "meta": [
        {
            "kind": "Unit",
            "name": "psi",
            "persistableReference": "{\"abcd\":{\"a\":0.0,\"b\":4.4482216152605,\"c\":0.00064516,\"d\":0.0},\"symbol\":\"psi\",\"baseMeasurement\":{\"ancestry\":\"M/LT2\",\"type\":\"UM\"},\"type\":\"UAD\"}",
            "propertyNames": [
                "RCAMeasurements[].Conditions.Pressure"
            ],
            "unitOfMeasureID": "opendes:reference-data--UnitOfMeasure:psi:"
        },
        {
            "kind": "Unit",
            "name": "K",
            "persistableReference": "{\"abcd\":{\"a\":0.0,\"b\":1.0,\"c\":1.0,\"d\":0.0},\"symbol\":\"K\",\"baseMeasurement\":{\"ancestry\":\"K\",\"type\":\"UM\"},\"type\":\"UAD\"}",
            "propertyNames": [
                "RCAMeasurements[].Conditions.Temperature"
            ],
            "unitOfMeasureID": "opendes:reference-data--UnitOfMeasure:K:"
        },
        {
            "kind": "Unit",
            "name": "m",
            "persistableReference": "{\"abcd\":{\"a\":0.0,\"b\":1.0,\"c\":1.0,\"d\":0.0},\"symbol\":\"m\",\"baseMeasurement\":{\"ancestry\":\"L\",\"type\":\"UM\"},\"type\":\"UAD\"}",
            "propertyNames": [
                "TopDepth",
                "BottomDepth"
            ],
            "unitOfMeasureID": "opendes:reference-data--UnitOfMeasure:m:"
        },
        {
            "kind": "Unit",
            "name": "mD",
            "persistableReference": "{\"abcd\":{\"a\":0.0,\"b\":1e-15,\"c\":1.01325,\"d\":0.0},\"symbol\":\"mD\",\"baseMeasurement\":{\"ancestry\":\"L2\",\"type\":\"UM\"},\"type\":\"UAD\"}",
            "propertyNames": [
                "RCAMeasurements[].Permeability"
            ],
            "unitOfMeasureID": "opendes:reference-data--UnitOfMeasure:mD:"
        },
        {
            "kind": "Unit",
            "name": "%",
            "persistableReference": "{\"abcd\":{\"a\":0.0,\"b\":0.01,\"c\":1.0,\"d\":0.0},\"symbol\":\"%\",\"baseMeasurement\":{\"ancestry\":\"1\",\"type\":\"UM\"},\"type\":\"UAD\"}",
            "propertyNames": [
                "RCAMeasurements[].Porosity"
            ],
            "unitOfMeasureID": "opendes:reference-data--UnitOfMeasure:%25:"
        },
        {
            "kind": "Unit",
            "name": "g/cm3",
            "persistableReference": "{\"abcd\":{\"a\":0.0,\"b\":1000.0,\"c\":1.0,\"d\":0.0},\"symbol\":\"g/cm3\",\"baseMeasurement\":{\"ancestry\":\"M/L3\",\"type\":\"UM\"},\"type\":\"UAD\"}",
            "propertyNames": [
                "RCAMeasurements[].GrainDensity"
            ],
            "unitOfMeasureID": "opendes:reference-data--UnitOfMeasure:g%2Fcm3:"
        }
    ]
}
```

</details>
