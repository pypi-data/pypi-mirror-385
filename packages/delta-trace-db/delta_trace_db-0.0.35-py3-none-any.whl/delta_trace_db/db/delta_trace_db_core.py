# coding: utf-8
from threading import RLock
from typing import Any, Dict, List, Callable, Optional

from file_state_manager.cloneable_file import CloneableFile

from delta_trace_db.db.delta_trace_db_collection import Collection
from delta_trace_db.query.cause.permission import Permission
from delta_trace_db.query.enum_query_type import EnumQueryType
from delta_trace_db.query.query import Query
from delta_trace_db.query.query_execution_result import QueryExecutionResult
from delta_trace_db.query.query_result import QueryResult
from delta_trace_db.query.transaction_query import TransactionQuery
from delta_trace_db.query.transaction_query_result import TransactionQueryResult
from delta_trace_db.query.util_query import UtilQuery
import logging

_logger = logging.getLogger(__name__)


class DeltaTraceDatabase(CloneableFile):
    class_name = "DeltaTraceDatabase"
    version = "12"

    def __init__(self):
        super().__init__()
        self._collections: Dict[str, Collection] = {}
        self._lock = RLock()  # execute_query / execute_transaction_query 共通

    @classmethod
    def from_dict(cls, src: Dict[str, Any]) -> "DeltaTraceDatabase":
        instance = cls()
        instance._collections = cls._parse_collections(src)
        return instance

    @staticmethod
    def _parse_collections(src: Dict[str, Any]) -> Dict[str, Collection]:
        cols = src.get("collections")
        if not isinstance(cols, dict):
            raise ValueError("Invalid format: 'collections' should be a dict")
        result: Dict[str, Collection] = {}
        for key, value in cols.items():
            if not isinstance(value, dict):
                raise ValueError("Invalid format: target is not a dict")
            result[key] = Collection.from_dict(value)
        return result

    def collection(self, name: str) -> Collection:
        with self._lock:
            if name in self._collections:
                return self._collections[name]
            col = Collection()
            self._collections[name] = col
            return col

    def find_collection(self, name: str) -> Optional[Collection]:
        """
        (en) Find the specified collection.
        Returns it if it exists, otherwise returns None.

        (ja) 指定のコレクションを検索します。
        存在すれば返し、存在しなければ None を返します。

        * name : The collection name.
        """
        with self._lock:
            return self._collections.get(name)

    def remove_collection(self, name: str) -> None:
        """
        (en) Deletes the specified collection.
        If a collection with the specified name does not exist, this does nothing.

        (ja) 指定のコレクションを削除します。
        指定の名前のコレクションが存在しなかった場合は何もしません。

        * name : The collection name.
        """
        with self._lock:
            self._collections.pop(name, None)

    def collection_to_dict(self, name: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            collection = self._collections.get(name)
            return collection.to_dict() if collection is not None else None

    def collection_from_dict(self, name: str, src: Dict[str, Any]) -> Collection:
        with self._lock:
            col = Collection.from_dict(src)
            self._collections[name] = col
            return col

    def collection_from_dict_keep_listener(self, name: str, src: Dict[str, Any]) -> Collection:
        """
        (en) Restores a specific collection from a dictionary, re-registers it,
        and retrieves it.
        If a collection with the same name already exists, it will be overwritten.
        This is typically used to restore data saved with collection_to_dict.
        This method preserves existing listeners when overwriting the specified
        collection.

        (ja) 特定のコレクションを辞書から復元して再登録し、取得します。
        既存の同名のコレクションが既にある場合は上書きされます。
        通常は、collection_to_dictで保存したデータを復元する際に使用します。
        このメソッドでは、指定されたコレクションの上書き時、既存のリスナが維持されます。

        * name : The collection name.
        * src : A dictionary made with collection_to_dict of this class.
        """
        with self._lock:
            col = Collection.from_dict(src)
            listeners_buf = None
            named_listeners_buf = None
            if name in self._collections:
                listeners_buf = getattr(self._collections[name], "listeners", None)
                named_listeners_buf = getattr(self._collections[name], "named_listeners", None)
            self._collections[name] = col
            if listeners_buf is not None:
                col.listeners = listeners_buf
            if named_listeners_buf is not None:
                col.named_listeners = named_listeners_buf
            return col

    def clone(self) -> "DeltaTraceDatabase":
        with self._lock:
            return DeltaTraceDatabase.from_dict(self.to_dict())

    @property
    def raw(self) -> Dict[str, Collection]:
        return self._collections

    def to_dict(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "className": self.class_name,
                "version": self.version,
                "collections": {k: v.to_dict() for k, v in self._collections.items()},
            }

    def add_listener(self, target: str, cb: Callable[[], None], name: Optional[str] = None):
        with self._lock:
            self.collection(target).add_listener(cb, name=name)

    def remove_listener(self, target: str, cb: Callable[[], None], name: Optional[str] = None):
        with self._lock:
            self.collection(target).remove_listener(cb, name=name)

    def execute_query_object(self, query: Any,
                             collection_permissions: Optional[Dict[str, Permission]] = None) -> QueryExecutionResult:
        with self._lock:  # 排他制御
            if isinstance(query, Query):
                return self.execute_query(query, collection_permissions=collection_permissions)
            elif isinstance(query, TransactionQuery):
                return self.execute_transaction_query(query, collection_permissions=collection_permissions)
            elif isinstance(query, dict):
                if query.get("className") == "Query":
                    return self.execute_query(Query.from_dict(query), collection_permissions=collection_permissions)
                elif query.get("className") == "TransactionQuery":
                    return self.execute_transaction_query(TransactionQuery.from_dict(query),
                                                          collection_permissions=collection_permissions)
                else:
                    raise ValueError("Unsupported query class")
            else:
                raise ValueError("Unsupported query type")

    def execute_query(self, q: Query, collection_permissions: Optional[Dict[str, Permission]] = None) -> QueryResult:
        with self._lock:  # 単体クエリもここで排他
            # パーミッションのチェック
            if not UtilQuery.check_permissions(q=q, collection_permissions=collection_permissions):
                return QueryResult(
                    is_success=False,
                    target=q.target,
                    type_=q.type,
                    result=[],
                    db_length=-1,
                    update_count=0,
                    hit_count=0,
                    error_message="Operation not permitted."
                )
            is_exist_col = q.target in self._collections
            col = self.collection(q.target)
            try:
                match q.type:
                    case EnumQueryType.add:
                        r = col.add_all(q)
                    case EnumQueryType.update:
                        r = col.update(q, is_single_target=False)
                    case EnumQueryType.updateOne:
                        r = col.update(q, is_single_target=True)
                    case EnumQueryType.delete:
                        r = col.delete(q)
                    case EnumQueryType.deleteOne:
                        r = col.delete_one(q)
                    case EnumQueryType.search:
                        r = col.search(q)
                    case EnumQueryType.searchOne:
                        r = col.search_one(q)
                    case EnumQueryType.getAll:
                        r = col.get_all(q)
                    case EnumQueryType.conformToTemplate:
                        r = col.conform_to_template(q)
                    case EnumQueryType.renameField:
                        r = col.rename_field(q)
                    case EnumQueryType.count:
                        r = col.count(q)
                    case EnumQueryType.clear:
                        r = col.clear(q)
                    case EnumQueryType.clearAdd:
                        r = col.clear_add(q)
                    case EnumQueryType.removeCollection:
                        if is_exist_col:
                            r = QueryResult(
                                is_success=True,
                                target=q.target,
                                type_=q.type,
                                result=[],
                                db_length=0,
                                update_count=1,
                                hit_count=0,
                                error_message=None)
                        else:
                            r = QueryResult(
                                is_success=True,
                                target=q.target,
                                type_=q.type,
                                result=[],
                                db_length=0,
                                update_count=0,
                                hit_count=0,
                                error_message=None)
                        self.remove_collection(name=q.target)
                # must_affect_at_least_oneの判定。
                if q.type in (
                        EnumQueryType.add,
                        EnumQueryType.update,
                        EnumQueryType.updateOne,
                        EnumQueryType.delete,
                        EnumQueryType.deleteOne,
                        EnumQueryType.conformToTemplate,
                        EnumQueryType.renameField,
                        EnumQueryType.clear,
                        EnumQueryType.clearAdd,
                        EnumQueryType.removeCollection
                ):
                    if q.must_affect_at_least_one and r.update_count == 0:
                        return QueryResult(
                            is_success=False,
                            target=q.target,
                            type_=q.type,
                            result=[],
                            db_length=len(col.raw),
                            update_count=0,
                            hit_count=r.hit_count,
                            error_message="No data matched the condition (mustAffectAtLeastOne=True)"
                        )
                return r
            except ValueError:
                # ここでは安全なメッセージのみを外部に返す
                _logger.error("execute_query ArgumentError", exc_info=True)
                return QueryResult(
                    is_success=False,
                    target=q.target,
                    type_=q.type,
                    result=[],
                    db_length=len(col.raw),
                    update_count=-1,
                    hit_count=-1,
                    error_message="execute_query ArgumentError"
                )
            except Exception:
                _logger.error("execute_query Unexpected Error", exc_info=True)
                return QueryResult(
                    is_success=False,
                    target=q.target,
                    type_=q.type,
                    result=[],
                    db_length=len(col.raw),
                    update_count=-1,
                    hit_count=-1,
                    error_message="execute_query Unexpected Error",
                )

    def execute_transaction_query(self, q: TransactionQuery,
                                  collection_permissions: Optional[
                                      Dict[str, Permission]] = None) -> TransactionQueryResult:
        with self._lock:  # トランザクション全体で排他
            # 許可されていないクエリが混ざっていないか調査し、混ざっていたら失敗にする。
            for i in q.queries:
                if i.type == EnumQueryType.removeCollection:
                    return TransactionQueryResult(is_success=False, results=[],
                                                  error_message="The query contains a type that is not permitted to be executed within a transaction.")
            # トランザクション付き処理を開始。
            results: List[QueryResult] = []
            try:
                buff: Dict[str, Dict[str, Any]] = {}
                non_exist_targets: set[str] = set()
                for i in q.queries:
                    if i.target in buff:
                        continue
                    else:
                        t_collection: Optional[dict[str, Any]] = self.collection_to_dict(i.target)
                        if t_collection is not None:
                            buff[i.target] = t_collection
                            # コレクションをトランザクションモードに変更する。
                            self.collection(i.target).change_transaction_mode(True)
                        else:
                            non_exist_targets.add(i.target)
                try:
                    for i in q.queries:
                        results.append(self.execute_query(i, collection_permissions=collection_permissions))
                except Exception:
                    _logger.error("execute_transaction_query: Transaction failed", exc_info=True)
                    return self._rollback_collections(buff=buff, non_exist_targets=non_exist_targets)

                # rollback if any query failed
                if any(not r.is_success for r in results):
                    return self._rollback_collections(buff=buff, non_exist_targets=non_exist_targets)

                # commit: notify listeners
                for key in buff.keys():
                    col = self.collection(key)
                    need_callback = getattr(col, "run_notify_listeners_in_transaction", False)
                    col.change_transaction_mode(False)
                    if need_callback:
                        col.notify_listeners()
                return TransactionQueryResult(is_success=True, results=results)
            except Exception:
                _logger.error("execute_transaction_query: Transaction failed", exc_info=True)
                return TransactionQueryResult(is_success=False, results=[], error_message="Unexpected Error")

    def _rollback_collections(self,
                              buff: dict[str, dict[str, Any]],
                              non_exist_targets: set[str],
                              ) -> TransactionQueryResult:
        # DBの変更を元に戻す。
        for key in buff.keys():
            self.collection_from_dict_keep_listener(key, buff[key])
            # 念のため確実に false にする。
            self.collection(key).change_transaction_mode(False)
        # 操作前に存在しなかったコレクションは削除する。
        for key in non_exist_targets:
            self.remove_collection(key)
        _logger.error("execute_transaction_query: Transaction failed", exc_info=True)
        return TransactionQueryResult(
            is_success=False,
            results=[],
            error_message="Transaction failed",
        )
