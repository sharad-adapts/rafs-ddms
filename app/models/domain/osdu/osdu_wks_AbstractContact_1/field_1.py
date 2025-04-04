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
#   filename:  /api/schema-service/v1/schema/osdu:wks:master-data--Sample:1.0.0
#   timestamp: 2023-10-24T20:27:08+00:00

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, constr


class Field0(BaseModel):
    RoleTypeID: Optional[
        constr(
            regex=r"^[\w\-\.]+:reference-data\-\-ContactRoleType:[\w\-\.\:\%]+:[0-9]*$"
        )
    ] = Field(
        None,
        description="The identifier of a reference value for the role of the contact within the associated organisation, such as Account owner, Sales Representative, Technical Support, Project Manager, Party Chief, Client Representative, Senior Observer.",
        title="Role Type ID",
    )
    Comment: Optional[str] = Field(
        None, description="Additional information about the contact", title="Comment"
    )
    WorkflowPersonaTypeID: Optional[
        constr(
            regex=r"^[\w\-\.]+:reference-data\-\-WorkflowPersonaType:[\w\-\.\:\%]+:[0-9]*$"
        )
    ] = Field(
        None,
        description="The persona in context of workflows associated with this contact, as used in TechnicalAssurance.",
        title="WorkflowPersonaTypeID",
    )
    DataGovernanceRoleTypeID: Optional[
        constr(
            regex=r"^[\w\-\.]+:reference-data\-\-DataGovernanceRoleType:[\w\-\.\:\%]+:[0-9]*$"
        )
    ] = Field(
        None,
        description="The data governance role assigned to this contact if and only if the context has a data governance role (in context of TechnicalAssurance). The value is kept absent in all other cases.",
        title="DataGovernanceRoleTypeID",
    )
    OrganisationID: Optional[
        constr(regex=r"^[\w\-\.]+:master-data\-\-Organisation:[\w\-\.\:\%]+:[0-9]*$")
    ] = Field(
        None,
        description="Reference to the company the contact is associated with.",
        title="Organisation ID",
    )
    PhoneNumber: Optional[str] = Field(
        None,
        description="Contact phone number. Property may be left empty where it is inappropriate to provide personally identifiable information.",
        example="1-555-281-5555",
        title="Phone Number",
    )
    EmailAddress: Optional[str] = Field(
        None,
        description="Contact email address. Property may be left empty where it is inappropriate to provide personally identifiable information.",
        example="support@company.com",
        title="Email Address",
    )
    Name: Optional[str] = Field(
        None,
        description="Name of the individual contact. Property may be left empty where it is inappropriate to provide personally identifiable information.",
        title="Name",
    )
