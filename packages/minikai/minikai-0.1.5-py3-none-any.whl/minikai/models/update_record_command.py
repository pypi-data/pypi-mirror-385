from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime

if TYPE_CHECKING:
  from ..models.update_record_command_tags import UpdateRecordCommandTags
  from ..models.record_authorization_dto import RecordAuthorizationDto
  from ..models.record_relation_dto import RecordRelationDto





T = TypeVar("T", bound="UpdateRecordCommand")



@_attrs_define
class UpdateRecordCommand:
    """ 
        Attributes:
            id (Union[Unset, str]):
            title (Union[Unset, str]):
            description (Union[None, Unset, str]):
            event_date (Union[None, Unset, datetime.datetime]):
            schema (Union[Unset, Any]):
            content (Union[Unset, Any]):
            relations (Union[Unset, list['RecordRelationDto']]):
            external_uri (Union[None, Unset, str]):
            labels (Union[Unset, list[str]]):
            tags (Union[Unset, UpdateRecordCommandTags]):
            authorization (Union['RecordAuthorizationDto', None, Unset]):
            archived (Union[Unset, bool]):
     """

    id: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    event_date: Union[None, Unset, datetime.datetime] = UNSET
    schema: Union[Unset, Any] = UNSET
    content: Union[Unset, Any] = UNSET
    relations: Union[Unset, list['RecordRelationDto']] = UNSET
    external_uri: Union[None, Unset, str] = UNSET
    labels: Union[Unset, list[str]] = UNSET
    tags: Union[Unset, 'UpdateRecordCommandTags'] = UNSET
    authorization: Union['RecordAuthorizationDto', None, Unset] = UNSET
    archived: Union[Unset, bool] = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.update_record_command_tags import UpdateRecordCommandTags
        from ..models.record_authorization_dto import RecordAuthorizationDto
        from ..models.record_relation_dto import RecordRelationDto
        id = self.id

        title = self.title

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        event_date: Union[None, Unset, str]
        if isinstance(self.event_date, Unset):
            event_date = UNSET
        elif isinstance(self.event_date, datetime.datetime):
            event_date = self.event_date.isoformat()
        else:
            event_date = self.event_date

        schema = self.schema

        content = self.content

        relations: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.relations, Unset):
            relations = []
            for relations_item_data in self.relations:
                relations_item = relations_item_data.to_dict()
                relations.append(relations_item)



        external_uri: Union[None, Unset, str]
        if isinstance(self.external_uri, Unset):
            external_uri = UNSET
        else:
            external_uri = self.external_uri

        labels: Union[Unset, list[str]] = UNSET
        if not isinstance(self.labels, Unset):
            labels = self.labels



        tags: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags.to_dict()

        authorization: Union[None, Unset, dict[str, Any]]
        if isinstance(self.authorization, Unset):
            authorization = UNSET
        elif isinstance(self.authorization, RecordAuthorizationDto):
            authorization = self.authorization.to_dict()
        else:
            authorization = self.authorization

        archived = self.archived


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if title is not UNSET:
            field_dict["title"] = title
        if description is not UNSET:
            field_dict["description"] = description
        if event_date is not UNSET:
            field_dict["eventDate"] = event_date
        if schema is not UNSET:
            field_dict["schema"] = schema
        if content is not UNSET:
            field_dict["content"] = content
        if relations is not UNSET:
            field_dict["relations"] = relations
        if external_uri is not UNSET:
            field_dict["externalUri"] = external_uri
        if labels is not UNSET:
            field_dict["labels"] = labels
        if tags is not UNSET:
            field_dict["tags"] = tags
        if authorization is not UNSET:
            field_dict["authorization"] = authorization
        if archived is not UNSET:
            field_dict["archived"] = archived

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_record_command_tags import UpdateRecordCommandTags
        from ..models.record_authorization_dto import RecordAuthorizationDto
        from ..models.record_relation_dto import RecordRelationDto
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        title = d.pop("title", UNSET)

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_event_date(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                event_date_type_0 = isoparse(data)



                return event_date_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        event_date = _parse_event_date(d.pop("eventDate", UNSET))


        schema = d.pop("schema", UNSET)

        content = d.pop("content", UNSET)

        relations = []
        _relations = d.pop("relations", UNSET)
        for relations_item_data in (_relations or []):
            relations_item = RecordRelationDto.from_dict(relations_item_data)



            relations.append(relations_item)


        def _parse_external_uri(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        external_uri = _parse_external_uri(d.pop("externalUri", UNSET))


        labels = cast(list[str], d.pop("labels", UNSET))


        _tags = d.pop("tags", UNSET)
        tags: Union[Unset, UpdateRecordCommandTags]
        if isinstance(_tags,  Unset):
            tags = UNSET
        else:
            tags = UpdateRecordCommandTags.from_dict(_tags)




        def _parse_authorization(data: object) -> Union['RecordAuthorizationDto', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                authorization_type_0 = RecordAuthorizationDto.from_dict(data)



                return authorization_type_0
            except: # noqa: E722
                pass
            return cast(Union['RecordAuthorizationDto', None, Unset], data)

        authorization = _parse_authorization(d.pop("authorization", UNSET))


        archived = d.pop("archived", UNSET)

        update_record_command = cls(
            id=id,
            title=title,
            description=description,
            event_date=event_date,
            schema=schema,
            content=content,
            relations=relations,
            external_uri=external_uri,
            labels=labels,
            tags=tags,
            authorization=authorization,
            archived=archived,
        )

        return update_record_command

