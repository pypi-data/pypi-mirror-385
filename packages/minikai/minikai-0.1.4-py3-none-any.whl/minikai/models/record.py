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
  from ..models.record_relation import RecordRelation
  from ..models.record_authorization import RecordAuthorization
  from ..models.record_tag import RecordTag
  from ..models.record_attachment import RecordAttachment





T = TypeVar("T", bound="Record")



@_attrs_define
class Record:
    """ 
        Attributes:
            id (Union[Unset, str]):
            organization_id (Union[Unset, str]):
            title (Union[Unset, str]):
            description (Union[None, Unset, str]):
            created_at (Union[Unset, datetime.datetime]):
            updated_at (Union[Unset, datetime.datetime]):
            event_date (Union[None, Unset, datetime.datetime]):
            created_by (Union[Unset, str]):
            updated_by (Union[None, Unset, str]):
            searchable (Union[Unset, bool]):
            ttl (Union[None, Unset, int]):
            archived (Union[Unset, bool]):
            schema (Union[Unset, Any]):
            content (Union[Unset, Any]):
            content_text (Union[None, Unset, str]):
            attachments (Union[Unset, list['RecordAttachment']]):
            authorization (Union[Unset, RecordAuthorization]):
            relations (Union[Unset, list['RecordRelation']]):
            external_uri (Union[None, Unset, str]):
            labels (Union[Unset, list[str]]):
            tags (Union[Unset, list['RecordTag']]):
            field_etag (Union[None, Unset, str]):
     """

    id: Union[Unset, str] = UNSET
    organization_id: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    event_date: Union[None, Unset, datetime.datetime] = UNSET
    created_by: Union[Unset, str] = UNSET
    updated_by: Union[None, Unset, str] = UNSET
    searchable: Union[Unset, bool] = UNSET
    ttl: Union[None, Unset, int] = UNSET
    archived: Union[Unset, bool] = UNSET
    schema: Union[Unset, Any] = UNSET
    content: Union[Unset, Any] = UNSET
    content_text: Union[None, Unset, str] = UNSET
    attachments: Union[Unset, list['RecordAttachment']] = UNSET
    authorization: Union[Unset, 'RecordAuthorization'] = UNSET
    relations: Union[Unset, list['RecordRelation']] = UNSET
    external_uri: Union[None, Unset, str] = UNSET
    labels: Union[Unset, list[str]] = UNSET
    tags: Union[Unset, list['RecordTag']] = UNSET
    field_etag: Union[None, Unset, str] = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.record_relation import RecordRelation
        from ..models.record_authorization import RecordAuthorization
        from ..models.record_tag import RecordTag
        from ..models.record_attachment import RecordAttachment
        id = self.id

        organization_id = self.organization_id

        title = self.title

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        event_date: Union[None, Unset, str]
        if isinstance(self.event_date, Unset):
            event_date = UNSET
        elif isinstance(self.event_date, datetime.datetime):
            event_date = self.event_date.isoformat()
        else:
            event_date = self.event_date

        created_by = self.created_by

        updated_by: Union[None, Unset, str]
        if isinstance(self.updated_by, Unset):
            updated_by = UNSET
        else:
            updated_by = self.updated_by

        searchable = self.searchable

        ttl: Union[None, Unset, int]
        if isinstance(self.ttl, Unset):
            ttl = UNSET
        else:
            ttl = self.ttl

        archived = self.archived

        schema = self.schema

        content = self.content

        content_text: Union[None, Unset, str]
        if isinstance(self.content_text, Unset):
            content_text = UNSET
        else:
            content_text = self.content_text

        attachments: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.attachments, Unset):
            attachments = []
            for attachments_item_data in self.attachments:
                attachments_item = attachments_item_data.to_dict()
                attachments.append(attachments_item)



        authorization: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.authorization, Unset):
            authorization = self.authorization.to_dict()

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



        tags: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = []
            for tags_item_data in self.tags:
                tags_item = tags_item_data.to_dict()
                tags.append(tags_item)



        field_etag: Union[None, Unset, str]
        if isinstance(self.field_etag, Unset):
            field_etag = UNSET
        else:
            field_etag = self.field_etag


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if organization_id is not UNSET:
            field_dict["organizationId"] = organization_id
        if title is not UNSET:
            field_dict["title"] = title
        if description is not UNSET:
            field_dict["description"] = description
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at
        if event_date is not UNSET:
            field_dict["eventDate"] = event_date
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if updated_by is not UNSET:
            field_dict["updatedBy"] = updated_by
        if searchable is not UNSET:
            field_dict["searchable"] = searchable
        if ttl is not UNSET:
            field_dict["ttl"] = ttl
        if archived is not UNSET:
            field_dict["archived"] = archived
        if schema is not UNSET:
            field_dict["schema"] = schema
        if content is not UNSET:
            field_dict["content"] = content
        if content_text is not UNSET:
            field_dict["contentText"] = content_text
        if attachments is not UNSET:
            field_dict["attachments"] = attachments
        if authorization is not UNSET:
            field_dict["authorization"] = authorization
        if relations is not UNSET:
            field_dict["relations"] = relations
        if external_uri is not UNSET:
            field_dict["externalUri"] = external_uri
        if labels is not UNSET:
            field_dict["labels"] = labels
        if tags is not UNSET:
            field_dict["tags"] = tags
        if field_etag is not UNSET:
            field_dict["_etag"] = field_etag

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.record_relation import RecordRelation
        from ..models.record_authorization import RecordAuthorization
        from ..models.record_tag import RecordTag
        from ..models.record_attachment import RecordAttachment
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        organization_id = d.pop("organizationId", UNSET)

        title = d.pop("title", UNSET)

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))


        _created_at = d.pop("createdAt", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at,  Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)




        _updated_at = d.pop("updatedAt", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at,  Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)




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


        created_by = d.pop("createdBy", UNSET)

        def _parse_updated_by(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        updated_by = _parse_updated_by(d.pop("updatedBy", UNSET))


        searchable = d.pop("searchable", UNSET)

        def _parse_ttl(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        ttl = _parse_ttl(d.pop("ttl", UNSET))


        archived = d.pop("archived", UNSET)

        schema = d.pop("schema", UNSET)

        content = d.pop("content", UNSET)

        def _parse_content_text(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        content_text = _parse_content_text(d.pop("contentText", UNSET))


        attachments = []
        _attachments = d.pop("attachments", UNSET)
        for attachments_item_data in (_attachments or []):
            attachments_item = RecordAttachment.from_dict(attachments_item_data)



            attachments.append(attachments_item)


        _authorization = d.pop("authorization", UNSET)
        authorization: Union[Unset, RecordAuthorization]
        if isinstance(_authorization,  Unset):
            authorization = UNSET
        else:
            authorization = RecordAuthorization.from_dict(_authorization)




        relations = []
        _relations = d.pop("relations", UNSET)
        for relations_item_data in (_relations or []):
            relations_item = RecordRelation.from_dict(relations_item_data)



            relations.append(relations_item)


        def _parse_external_uri(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        external_uri = _parse_external_uri(d.pop("externalUri", UNSET))


        labels = cast(list[str], d.pop("labels", UNSET))


        tags = []
        _tags = d.pop("tags", UNSET)
        for tags_item_data in (_tags or []):
            tags_item = RecordTag.from_dict(tags_item_data)



            tags.append(tags_item)


        def _parse_field_etag(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        field_etag = _parse_field_etag(d.pop("_etag", UNSET))


        record = cls(
            id=id,
            organization_id=organization_id,
            title=title,
            description=description,
            created_at=created_at,
            updated_at=updated_at,
            event_date=event_date,
            created_by=created_by,
            updated_by=updated_by,
            searchable=searchable,
            ttl=ttl,
            archived=archived,
            schema=schema,
            content=content,
            content_text=content_text,
            attachments=attachments,
            authorization=authorization,
            relations=relations,
            external_uri=external_uri,
            labels=labels,
            tags=tags,
            field_etag=field_etag,
        )

        return record

