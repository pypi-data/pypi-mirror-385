# coding: utf-8
from typing import Any, Dict, List, Optional

from delta_trace_db.query.enum_query_type import EnumQueryType
from delta_trace_db.query.query_builder import QueryBuilder
from delta_trace_db.query.query import Query
from delta_trace_db.query.sort.abstract_sort import AbstractSort
from delta_trace_db.query.nodes.query_node import QueryNode
from delta_trace_db.query.cause.cause import Cause


class RawQueryBuilder(QueryBuilder):
    def __init__(
            self,
            target: str,
            type_: EnumQueryType,
            raw_add_data: Optional[List[Dict[str, Any]]] = None,
            override_data: Optional[Dict[str, Any]] = None,
            raw_template: Optional[Dict[str, Any]] = None,
            query_node: Optional[QueryNode] = None,
            sort_obj: Optional[AbstractSort] = None,
            offset: Optional[int] = None,
            start_after: Optional[Dict[str, Any]] = None,
            end_before: Optional[Dict[str, Any]] = None,
            rename_before: Optional[str] = None,
            rename_after: Optional[str] = None,
            limit: Optional[int] = None,
            return_data: Optional[bool] = None,
            must_affect_at_least_one: bool = True,
            serial_key: Optional[str] = None,
            reset_serial: bool = False,
            cause: Optional[Cause] = None,
    ):
        super().__init__(
            target=target,
            type_=type_,
            override_data=override_data,
            query_node=query_node,
            sort_obj=sort_obj,
            offset=offset,
            start_after=start_after,
            end_before=end_before,
            rename_before=rename_before,
            rename_after=rename_after,
            limit=limit,
            return_data=return_data,
            must_affect_at_least_one=must_affect_at_least_one,
            serial_key=serial_key,
            reset_serial=reset_serial,
            cause=cause
        )
        self.raw_add_data = raw_add_data
        self.raw_template = raw_template

    @classmethod
    def add(cls, target: str, raw_add_data: List[Dict[str, Any]],
            return_data: bool = False,
            must_affect_at_least_one: bool = True,
            serial_key: Optional[str] = None,
            cause: Optional[Cause] = None):
        return cls(target=target, type_=EnumQueryType.add, raw_add_data=raw_add_data,
                   return_data=return_data,
                   must_affect_at_least_one=must_affect_at_least_one,
                   serial_key=serial_key,
                   cause=cause)

    @classmethod
    def update(
            cls,
            target: str,
            query_node: QueryNode,
            override_data: Optional[Dict[str, Any]],
            return_data: bool = False,
            sort_obj: Optional[AbstractSort] = None,
            must_affect_at_least_one: bool = True,
            cause: Optional[Cause] = None
    ):
        return cls(
            target=target,
            type_=EnumQueryType.update,
            query_node=query_node,
            override_data=override_data,
            return_data=return_data,
            sort_obj=sort_obj,
            must_affect_at_least_one=must_affect_at_least_one,
            cause=cause
        )

    @classmethod
    def update_one(
            cls,
            target: str,
            query_node: QueryNode,
            override_data: Optional[Dict[str, Any]],
            return_data: bool = False,
            must_affect_at_least_one: bool = True,
            cause: Optional[Cause] = None
    ):
        return cls(
            target=target,
            type_=EnumQueryType.updateOne,
            query_node=query_node,
            override_data=override_data,
            return_data=return_data,
            must_affect_at_least_one=must_affect_at_least_one,
            cause=cause
        )

    @classmethod
    def delete(
            cls,
            target: str,
            query_node: QueryNode,
            return_data: bool = False,
            sort_obj: Optional[AbstractSort] = None,
            must_affect_at_least_one: bool = True,
            cause: Optional[Cause] = None
    ):
        return cls(
            target=target,
            type_=EnumQueryType.delete,
            query_node=query_node,
            return_data=return_data,
            sort_obj=sort_obj,
            must_affect_at_least_one=must_affect_at_least_one,
            cause=cause
        )

    @classmethod
    def delete_one(
            cls,
            target: str,
            query_node: QueryNode,
            return_data: bool = False,
            must_affect_at_least_one: bool = True,
            cause: Optional[Cause] = None
    ):
        return cls(
            target=target,
            type_=EnumQueryType.deleteOne,
            query_node=query_node,
            return_data=return_data,
            must_affect_at_least_one=must_affect_at_least_one,
            cause=cause
        )

    @classmethod
    def search(
            cls,
            target: str,
            query_node: QueryNode,
            sort_obj: Optional[AbstractSort] = None,
            offset: Optional[int] = None,
            start_after: Optional[Dict[str, Any]] = None,
            end_before: Optional[Dict[str, Any]] = None,
            limit: Optional[int] = None,
            cause: Optional[Cause] = None
    ):
        return cls(
            target=target,
            type_=EnumQueryType.search,
            query_node=query_node,
            sort_obj=sort_obj,
            offset=offset,
            start_after=start_after,
            end_before=end_before,
            limit=limit,
            cause=cause
        )

    @classmethod
    def search_one(
            cls,
            target: str,
            query_node: QueryNode,
            cause: Optional[Cause] = None
    ):
        return cls(
            target=target,
            type_=EnumQueryType.searchOne,
            query_node=query_node,
            cause=cause
        )

    @classmethod
    def get_all(cls, target: str, sort_obj: Optional[AbstractSort] = None, offset: Optional[int] = None,
                start_after: Optional[Dict[str, Any]] = None,
                end_before: Optional[Dict[str, Any]] = None,
                limit: Optional[int] = None, cause: Optional[Cause] = None):
        return cls(target=target, type_=EnumQueryType.getAll, sort_obj=sort_obj, offset=offset, start_after=start_after,
                   end_before=end_before, limit=limit, cause=cause)

    @classmethod
    def conform_to_template(
            cls,
            target: str,
            raw_template: Optional[Dict[str, Any]] = None,
            must_affect_at_least_one: bool = True,
            cause: Optional[Cause] = None
    ):
        return cls(
            target=target,
            type_=EnumQueryType.conformToTemplate,
            raw_template=raw_template,
            must_affect_at_least_one=must_affect_at_least_one,
            cause=cause
        )

    @classmethod
    def rename_field(
            cls,
            target: str,
            rename_before: str,
            rename_after: str,
            return_data: bool = False,
            must_affect_at_least_one: bool = True,
            cause: Optional[Cause] = None
    ):
        return cls(
            target=target,
            type_=EnumQueryType.renameField,
            rename_before=rename_before,
            rename_after=rename_after,
            return_data=return_data,
            must_affect_at_least_one=must_affect_at_least_one,
            cause=cause
        )

    @classmethod
    def count(cls, target: str, cause: Optional[Cause] = None):
        return cls(target=target, type_=EnumQueryType.count, cause=cause)

    @classmethod
    def clear(cls, target: str, must_affect_at_least_one: bool = True, reset_serial: bool = False,
              cause: Optional[Cause] = None):
        return cls(target=target, type_=EnumQueryType.clear, must_affect_at_least_one=must_affect_at_least_one,
                   reset_serial=reset_serial,
                   cause=cause)

    @classmethod
    def clear_add(cls, target: str, raw_add_data: List[Dict[str, Any]],
                  return_data: bool = False,
                  must_affect_at_least_one: bool = True,
                  serial_key: Optional[str] = None,
                  reset_serial: bool = False,
                  cause: Optional[Cause] = None):
        return cls(target=target, type_=EnumQueryType.clearAdd, raw_add_data=raw_add_data,
                   return_data=return_data,
                   must_affect_at_least_one=must_affect_at_least_one,
                   serial_key=serial_key,
                   reset_serial=reset_serial,
                   cause=cause)

    @classmethod
    def remove_collection(cls, target: str,
                          must_affect_at_least_one: bool = True,
                          cause: Optional[Cause] = None):
        return cls(target, EnumQueryType.removeCollection,
                   must_affect_at_least_one=must_affect_at_least_one,
                   cause=cause)

    def set_offset(self, new_offset: Optional[int]):
        self.offset = new_offset
        return self

    def set_start_after(self, new_start_after: Optional[Dict[str, Any]]):
        self.start_after = new_start_after
        return self

    def set_end_before(self, new_end_before: Optional[Dict[str, Any]]):
        self.end_before = new_end_before
        return self

    def set_limit(self, new_limit: Optional[int]):
        self.limit = new_limit
        return self

    def build(self) -> Query:
        return Query(
            target=self.target,
            type_=self.type,
            add_data=self.raw_add_data,
            override_data=self.override_data,
            template=self.raw_template,
            query_node=self.query_node,
            sort_obj=self.sort_obj,
            offset=self.offset,
            start_after=self.start_after,
            end_before=self.end_before,
            rename_before=self.rename_before,
            rename_after=self.rename_after,
            limit=self.limit,
            return_data=self.return_data,
            must_affect_at_least_one=self.must_affect_at_least_one,
            serial_key=self.serial_key,
            reset_serial=self.reset_serial,
            cause=self.cause
        )
