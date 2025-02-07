## Pydantic Model Generator for Rafs

The `model_generator.py` script generates Pydantic models from JSON schemas with a specific naming convention, customized for use with Rafs. It also incorporates versioning information from the file names.

**Features:**

* Generates Pydantic models from JSON schemas.
* Filters schemas based on a file name ending (e.g., `1.0.0.json`).
* Extracts version information (major, minor, patch) from the file name.
* Replaces `pydantic.BaseModel` with `RafsBaseModel` for Rafs compatibility.
* Updates the model class name based on the schema name and version information.
* Adds copyright notice and imports RafsBaseModel.

**Requirements:**

* Python 3.x
* `datamodel-code-generator` package

**Usage:**

1. Install `datamodel-code-generator`:

   ```bash
   pip install datamodel-code-generator
   ```

2. Run the script:

   If there is an unproccesed schema with format `AnalysisTypeDataSchema.1.0.0.json` please first run
   ```bash
   python process_schemas.py <source_directory> <end_filter>
   ```
   - `<source_directory>`: Path to the directory containing JSON schemas.
   - `<end_filter>` (Optional): Filter for schema file names (defaults to `DataSchema.1.0.0.json`).

   Then run:

   ```bash
   python model_generator.py <source_directory> <target_directory> [<end_filter>]
   ```

   - `<source_directory>`: Path to the directory containing JSON schemas.
   - `<target_directory>`: Path to the output directory for generated Pydantic models.
   - `<end_filter>` (Optional): Filter for schema file names (defaults to `1.0.0.json`).

**Example run:**

```bash
python scripts/process_schemas.py /path/to/schemas  DataSchema.1.0.0.json

python scripts/model_generator.py /path/to/schemas /path/to/models 1.0.0.json
```

This will generate Pydantic models from all files ending in `1.0.0.json` in the `/path/to/schemas` directory and write them to the `/path/to/models` directory, incorporating the version information into the model class name.

**Copyright:**

The script includes the provided copyright notice for ExxonMobil Technology and Engineering Company with the Apache License 2.0.

**Additional Notes:**

* The script assumes a specific naming convention for JSON schema files: `AnalysisTypeDataSchema.Major.Minor.Patch.json`. You can modify the regular expression to match your specific naming format.
* For debugging purposes, the script prints the generated command before executing it.

## Test data validator

The `test_data_validator.py` script validates example data against the created data model and creates the `test_data_orient_split.json` to use in tests.

**Source Data Example**

The source data example should be in pandas orient="records" format. Hint: just enclose the json object in an array.

**AnalysisType Model Class Name**

The class name of the pydantic model to use for validation. Can be found in [app/models/data_schemas/api_v2/base.py](../app/models/data_schemas/api_v2/base.py)

**Example run:**

```bash
python scripts/test_data_validator.py /path/to/example.json /path/to/test_data_orient_split.json AnalysisTypeModelClassName
```

This will generate Pydantic models from all files ending in `DataSchema.1.0.0.json` in the `/path/to/schemas` directory and write them to the `/path/to/models` directory, incorporating the version information into the model class name.
