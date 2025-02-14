# RAFS DDMS Framework
Rock and Fluid Sample Domain Data Management Services (RAFS DDMS) Open Subsurface Data Universe (OSDU) is a microservices-based project that comprises OSDU software ecosystem, written in Python that provides an API for managing Rock and Fluid Sample related data.

## Context Overview
![RSAFDDMS_Flow_-_Overview](./rafs_ddms_flow_overview.png)

> **Note:** The Parsers are outside the DDMS scope. Due to the different formats of the Sample Analysis Report files, each client must provide parsed bulk data as input for the RAFS DDMS `data endpoints.

## Components Overview
![RAFSDDMS_Components_-_Overview](./rafs_ddms_components.png)

> **Note:** the DDMS uses Dataset Service only for the legacy implementation — more details [here](https://community.opengroup.org/osdu/platform/domain-data-mgmt-services/rock-and-fluid-sample/rafs-ddms-services/-/issues/370).

### Web Server Overview
Technologies:
1. Python
  - `pandas` - bulk data (dataset) operation and management
  - `pandera` - bulkdata validation
  - `pydantic` - definition of data models
2. Redis (or CSP managed-solution) for caching and extended search index.
3. JSON-schema standard is used for the preliminary content schemas representation.

### Content schemas
As of the M25 release, the DDMS has not introduced the content schema registry for schema management.
The OSDU data definition team provides all content schemas in `JSON-schema` format.
Each schema has its data kind and is referenced to the appropriate `SampleAnalysis` WPC kind. Each schema file also has its version, e.g., `1.0.0`.

The RAFS DDMS comes with the data model generation script, which converts the JSON-schema files to the `pydantic` data model `py` files.

### Data persistence format
Parquet data format is used for data storage in the persistence zone.

The team also considered the following alternatives: ORC, Avro, Arrow, CSV, and JSON, and the following benefits of the Parquet format were taken into account:
1. Efficient compression
2. Fast query performance
3. Schema enforcement
4. Data partitioning
5. Compatibility with multiple Python libraries for data management (pandas, DuckDB, pySpark, etc.)
6. Support for complex data types
