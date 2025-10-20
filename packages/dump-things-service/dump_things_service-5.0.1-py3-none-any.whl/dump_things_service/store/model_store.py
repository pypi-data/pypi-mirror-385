from __future__ import annotations

from datetime import datetime
from itertools import chain
from typing import TYPE_CHECKING

from dump_things_service.model import (
    get_model_for_schema,
    get_subclasses,
)
from dump_things_service.resolve_curie import resolve_curie, is_curie
from dump_things_service.utils import cleaned_json

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pydantic import BaseModel

    from dump_things_service.backends import (
        RecordInfo,
        StorageBackend,
    )
    from dump_things_service.lazy_list import LazyList


submitter_class = 'NCIT_C54269'
submitter_namespace = 'http://purl.obolibrary.org/obo/'


class _ModelStore:
    def __init__(
        self,
        schema: str,
        backend: StorageBackend,
        tags: dict[str, str]
    ):
        self.schema = schema
        self.model = get_model_for_schema(self.schema)[0]
        self.backend = backend
        self.tags = tags

    def get_uri(self) -> str:
        return self.backend.get_uri()

    def store_object(
        self,
        obj: BaseModel,
        submitter: str,
    ) -> Iterable[tuple[str, dict]]:
        if obj.__class__.__name__ == 'Thing':
            msg = f'Cannot store `Thing` instance: {obj}.'
            raise ValueError(msg)

        # Extract inlined records from the object, store individual records
        # and return the list of stored records.
        return [
            (
                obj.__class__.__name__,
                self._store_flat_object(
                    obj=obj,
                    submitter=submitter,
                ),
            )
            for obj in self.extract_inlined(obj)
        ]

    def pid_to_iri(
        self,
        pid: str,
    ):
        return resolve_curie(self.model, pid)

    def _store_flat_object(
        self,
        obj: BaseModel,
        submitter: str,
    ) -> dict:
        iri = self.pid_to_iri(obj.pid)
        class_name = obj.__class__.__name__

        json_object = cleaned_json(
            obj.model_dump(exclude_none=True, mode='json'),
            remove_keys=('@type',),
        )

        # Add the submitter id to the record annotations
        self.annotate(json_object, submitter)
        self.backend.add_record(
            iri=iri,
            class_name=class_name,
            json_object=json_object,
        )
        return json_object

    def annotate(
        self,
        json_object: dict,
        submitter: str,
    ) -> None:
        """Add submitter IRI to the record annotations, use CURIE if possible"""
        if 'annotations' not in json_object:
            json_object['annotations'] = {}
        submitter_curie_or_iri = self.get_curie(self.tags['id'])
        time_curie_or_iri = self.get_curie(self.tags['time'])
        json_object['annotations'][submitter_curie_or_iri] = submitter
        json_object['annotations'][time_curie_or_iri] = datetime.now().isoformat()

    def get_curie(
        self,
        curie_or_iri: str,
    ) -> str:
        if is_curie(curie_or_iri):
            return curie_or_iri
        prefixes = self.model.linkml_meta.root.get('prefixes')
        if prefixes:
            for prefix_info in prefixes.values():
                reference = prefix_info['prefix_reference']
                if curie_or_iri.startswith(reference):
                    return curie_or_iri.replace(
                        reference,
                        prefix_info['prefix_prefix'] + ':',
                        1,
                    )
        return curie_or_iri

    def extract_inlined(
        self,
        record: BaseModel,
    ) -> list[BaseModel]:
        # The trivial case: no relations
        if not hasattr(record, 'relations') or record.relations is None:
            return [record]

        extracted_sub_records = list(
            chain(
                *[
                    self.extract_inlined(sub_record)
                    for sub_record in record.relations.values()
                    # Do not extract 'empty'-Thing records, those are just
                    # placeholders for already extracted records.
                    if sub_record != self.model.Thing(pid=sub_record.pid)
                ]
            )
        )
        # Simplify the relations in this record. We use "empty" Thing objects
        # as placeholders for extracted records.
        new_record = record.model_copy()
        new_record.relations = {
            sub_record_pid: self.model.Thing(pid=sub_record_pid)
            for sub_record_pid in record.relations
        }
        return [new_record, *extracted_sub_records]

    def get_object_by_pid(
        self,
        pid: str,
    ) -> tuple[str, dict] | tuple[None, None]:
        return self.get_object_by_iri(self.pid_to_iri(pid))

    def get_object_by_iri(
        self,
        iri: str,
    ) -> tuple[str, dict] | tuple[None, None]:
        record_info = self.backend.get_record_by_iri(iri)
        if record_info:
            return record_info.class_name, record_info.json_object
        return None, None

    def get_objects_of_class(
        self,
        class_name: str,
        matching: str | None,
        *,
        include_subclasses: bool = True,
    ) -> LazyList[RecordInfo]:
        """
        Get all objects of a specific class.

        :param class_name: The name of the class to filter by.
        :param matching: Return only records with a value that matches `matching`.
        :param include_subclasses: If `True`, return records of class `class_name`
            and its subclasses, if `False` return only records of class
            `class_name`.
        :return: A lazy list of objects of the specified class and its subclasses.
        """
        if include_subclasses:
            class_names = get_subclasses(self.model, class_name)
        else:
            class_names = [class_name]
        return self.backend.get_records_of_classes(class_names, matching)

    def get_all_objects(
        self,
        matching: str | None = None,
    ) -> LazyList[RecordInfo]:
        """
        Get all objects of a specific class.

        :param matching: Return only records with a value that matches `matching`.
        :return: A lazy list of all objects in the store.
        """
        return self.backend.get_all_records(matching)

    def delete_object(
        self,
        pid: str,
    ) -> bool:
        return self.backend.remove_record(self.pid_to_iri(pid))


_existing_model_stores = {}


def ModelStore(  # noqa: N802
    schema: str,
    backend: StorageBackend,
    tags: dict[str, str],
) -> _ModelStore:
    """
    Create a unique model store for the given schema and backend.

    :param schema: The schema to use for the model store.
    :param backend: The storage backend to use.
    :return: An instance of _ModelStore.
    """
    existing_model_store, _ = _existing_model_stores.get(id(backend), (None, None))
    if not existing_model_store:
        existing_model_store = _ModelStore(schema, backend, tags)
        # We store a pointer to the backend in the value to ensure that the
        # backend object exists while we use its `id` as a key.
        _existing_model_stores[id(backend)] = existing_model_store, backend
    return existing_model_store
