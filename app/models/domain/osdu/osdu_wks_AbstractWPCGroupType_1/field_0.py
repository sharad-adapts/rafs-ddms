#  Copyright 2023 ExxonMobil Technology and Engineering Company
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

# generated by datamodel-codegen:
#   filename:  /api/schema-service/v1/schema/osdu:wks:work-product-component--MultiStageSeparatorTest:1.0.0
#   timestamp: 2023-04-11T05:01:11+00:00

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, constr

from ..osdu_wks_AbstractTechnicalAssurance_1 import field_0


class Artefact(BaseModel):
    ResourceID: Optional[
        constr(regex=r'^[\w\-\.]+:dataset\-\-[\w\-\.]+:[\w\-\.\:\%]+:[0-9]*$')
    ] = Field(None, description='The SRN which identifies this OSDU Artefact resource.')
    ResourceKind: Optional[
        constr(regex=r'^[\w\-\.]+:[\w\-\.]+:[\w\-\.]+:[0-9]+.[0-9]+.[0-9]+$')
    ] = Field(
        None,
        description='The kind or schema ID of the artefact. Resolvable with the Schema Service.',
    )
    RoleID: Optional[
        constr(regex=r'^[\w\-\.]+:reference-data\-\-ArtefactRole:[\w\-\.\:\%]+:[0-9]*$')
    ] = Field(None, description="The SRN of this artefact's role.")


class Field0(BaseModel):
    Datasets: Optional[
        List[constr(regex=r'^[\w\-\.]+:dataset\-\-[\w\-\.]+:[\w\-\.\:\%]+:[0-9]*$')]
    ] = Field(
        None,
        description='The record id, which identifies this OSDU File or dataset resource.',
    )
    IsDiscoverable: Optional[bool] = Field(
        None,
        description='A flag that indicates if the work product component is searchable, which means covered in the search index.',
    )
    TechnicalAssurances: Optional[List[field_0.Field0]] = Field(
        None,
        description='Describes a record\'s overall suitability for general business consumption based on data quality. Clarifications: Since Certified is the highest classification of suitable quality, any further change or versioning of a Certified record should be carefully considered and justified. If a Technical Assurance value is not populated then one can assume the data has not been evaluated or its quality is unknown (=Unevaluated). Technical Assurance values are not intended to be used for the identification of a single "preferred" or "definitive" record by comparison with other records.',
        title='Technical Assurances',
    )
    Artefacts: Optional[List[Artefact]] = Field(
        None,
        description='An array of Artefacts - each artefact has a Role, Resource tuple. An artefact is distinct from the file, in the sense certain valuable information is generated during loading process (Artefact generation process). Examples include retrieving location data, performing an OCR which may result in the generation of artefacts which need to be preserved distinctly',
    )
    IsExtendedLoad: Optional[bool] = Field(
        None,
        description='A flag that indicates if the work product component is undergoing an extended load.  It reflects the fact that the work product component is in an early stage and may be updated before finalization.',
    )
