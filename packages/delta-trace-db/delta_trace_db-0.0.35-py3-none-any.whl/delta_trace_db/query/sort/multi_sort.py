# coding: utf-8
from typing import Any, Callable, Dict, List
from delta_trace_db.query.sort.abstract_sort import AbstractSort
from delta_trace_db.query.sort.single_sort import SingleSort

class MultiSort(AbstractSort):
    class_name = "MultiSort"
    version = "1"

    def __init__(self, sort_orders: List[SingleSort]):
        self.sort_orders = sort_orders

    @classmethod
    def from_dict(cls, src: Dict[str, Any]) -> "MultiSort":
        orders = [SingleSort.from_dict(e) for e in src.get("sortOrders", [])]
        return cls(orders)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "className": self.class_name,
            "version": self.version,
            "sortOrders": [s.to_dict() for s in self.sort_orders],
        }

    def get_comparator(self) -> Callable[[Dict[str, Any], Dict[str, Any]], int]:
        def comparator(a: Dict[str, Any], b: Dict[str, Any]) -> int:
            for sort_obj in self.sort_orders:
                comp = sort_obj.get_comparator()(a, b)
                if comp != 0:
                    return comp
            return 0
        return comparator
