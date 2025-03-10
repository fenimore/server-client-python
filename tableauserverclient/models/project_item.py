import logging
import xml.etree.ElementTree as ET
from typing import Optional

from defusedxml.ElementTree import fromstring

from tableauserverclient.models.exceptions import UnpopulatedPropertyError
from tableauserverclient.models.property_decorators import property_is_enum, property_not_empty


class ProjectItem:
    """
    The project resources for Tableau are defined in the ProjectItem class. The
    class corresponds to the project resources you can access using the Tableau
    Server REST API.

    Parameters
    ----------
    name : str
        Name of the project.

    description : str
        Description of the project.

    content_permissions : str
        Sets or shows the permissions for the content in the project. The
        options are either LockedToProject, ManagedByOwner or
        LockedToProjectWithoutNested.

    parent_id : str
        The id of the parent project. Use this option to create project
        hierarchies. For information about managing projects, project
        hierarchies, and permissions, see
        https://help.tableau.com/current/server/en-us/projects.htm

    samples : bool
        Set to True to include sample workbooks and data sources in the
        project. The default is False.

    Attributes
    ----------
    id : str
        The unique identifier for the project.

    owner_id : str
        The unique identifier for the UserItem owner of the project.

    """

    ERROR_MSG = "Project item must be populated with permissions first."

    class ContentPermissions:
        LockedToProject: str = "LockedToProject"
        ManagedByOwner: str = "ManagedByOwner"
        LockedToProjectWithoutNested: str = "LockedToProjectWithoutNested"

    def __repr__(self):
        return "<Project {} {} parent={} permissions={}>".format(
            self._id, self.name, self.parent_id or "None (Top level)", self.content_permissions or "Not Set"
        )

    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        content_permissions: Optional[str] = None,
        parent_id: Optional[str] = None,
        samples: Optional[bool] = None,
    ) -> None:
        self._content_permissions = None
        self._id: Optional[str] = None
        self.description: Optional[str] = description
        self.name: str = name
        self.content_permissions: Optional[str] = content_permissions
        self.parent_id: Optional[str] = parent_id
        self._samples: Optional[bool] = samples
        self._owner_id: Optional[str] = None

        self._permissions = None
        self._default_workbook_permissions = None
        self._default_datasource_permissions = None
        self._default_flow_permissions = None
        self._default_lens_permissions = None
        self._default_datarole_permissions = None
        self._default_metric_permissions = None
        self._default_virtualconnection_permissions = None
        self._default_database_permissions = None
        self._default_table_permissions = None

    @property
    def content_permissions(self):
        return self._content_permissions

    @content_permissions.setter
    @property_is_enum(ContentPermissions)
    def content_permissions(self, value: Optional[str]) -> None:
        self._content_permissions = value

    @property
    def permissions(self):
        if self._permissions is None:
            raise UnpopulatedPropertyError(self.ERROR_MSG)
        return self._permissions()

    @property
    def default_datasource_permissions(self):
        if self._default_datasource_permissions is None:
            raise UnpopulatedPropertyError(self.ERROR_MSG)
        return self._default_datasource_permissions()

    @property
    def default_workbook_permissions(self):
        if self._default_workbook_permissions is None:
            raise UnpopulatedPropertyError(self.ERROR_MSG)
        return self._default_workbook_permissions()

    @property
    def default_flow_permissions(self):
        if self._default_flow_permissions is None:
            raise UnpopulatedPropertyError(self.ERROR_MSG)
        return self._default_flow_permissions()

    @property
    def default_lens_permissions(self):
        if self._default_lens_permissions is None:
            raise UnpopulatedPropertyError(self.ERROR_MSG)
        return self._default_lens_permissions()

    @property
    def default_datarole_permissions(self):
        if self._default_datarole_permissions is None:
            raise UnpopulatedPropertyError(self.ERROR_MSG)
        return self._default_datarole_permissions()

    @property
    def default_metric_permissions(self):
        if self._default_metric_permissions is None:
            raise UnpopulatedPropertyError(self.ERROR_MSG)
        return self._default_metric_permissions()

    @property
    def default_virtualconnection_permissions(self):
        if self._default_virtualconnection_permissions is None:
            raise UnpopulatedPropertyError(self.ERROR_MSG)
        return self._default_virtualconnection_permissions()

    @property
    def default_database_permissions(self):
        if self._default_database_permissions is None:
            raise UnpopulatedPropertyError(self.ERROR_MSG)
        return self._default_database_permissions()

    @property
    def default_table_permissions(self):
        if self._default_table_permissions is None:
            raise UnpopulatedPropertyError(self.ERROR_MSG)
        return self._default_table_permissions()

    @property
    def id(self) -> Optional[str]:
        return self._id

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def owner_id(self) -> Optional[str]:
        return self._owner_id

    @owner_id.setter
    def owner_id(self, value: str) -> None:
        self._owner_id = value

    def is_default(self):
        return self.name.lower() == "default"

    def _parse_common_tags(self, project_xml, ns):
        if not isinstance(project_xml, ET.Element):
            project_xml = fromstring(project_xml).find(".//t:project", namespaces=ns)

        if project_xml is not None:
            (
                _,
                name,
                description,
                content_permissions,
                parent_id,
            ) = self._parse_element(project_xml)
            self._set_values(None, name, description, content_permissions, parent_id)
        return self

    def _set_values(self, project_id, name, description, content_permissions, parent_id, owner_id):
        if project_id is not None:
            self._id = project_id
        if name:
            self._name = name
        if description:
            self.description = description
        if content_permissions:
            self._content_permissions = content_permissions
        if parent_id:
            self.parent_id = parent_id
        if owner_id:
            self._owner_id = owner_id

    def _set_permissions(self, permissions):
        self._permissions = permissions

    def _set_default_permissions(self, permissions, content_type):
        attr = f"_default_{content_type}_permissions".lower()
        setattr(
            self,
            attr,
            permissions,
        )

    @classmethod
    def from_response(cls, resp, ns) -> list["ProjectItem"]:
        all_project_items = list()
        parsed_response = fromstring(resp)
        all_project_xml = parsed_response.findall(".//t:project", namespaces=ns)

        for project_xml in all_project_xml:
            project_item = cls.from_xml(project_xml)
            all_project_items.append(project_item)
        return all_project_items

    @classmethod
    def from_xml(cls, project_xml, namespace=None) -> "ProjectItem":
        project_item = cls()
        project_item._set_values(*cls._parse_element(project_xml))
        return project_item

    @staticmethod
    def _parse_element(project_xml):
        id = project_xml.get("id", None)
        name = project_xml.get("name", None)
        description = project_xml.get("description", None)
        content_permissions = project_xml.get("contentPermissions", None)
        parent_id = project_xml.get("parentProjectId", None)
        owner_id = None
        for owner in project_xml:
            owner_id = owner.get("id", None)

        return id, name, description, content_permissions, parent_id, owner_id
