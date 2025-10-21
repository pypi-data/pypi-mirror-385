from typing import List, Callable

import requests
from pydantic import BaseModel, parse_raw_as, PrivateAttr

from brevettiai.datamodel import DatasetItem, DatasetItemMetadata, DatasetObject

__all__ = ["DatasetItemMetadata"]


def _to_camel(x):
    init, *fol = x.split("_")
    if init:
        init = init[0].lower() + init[1:]
    return "".join((init, *map(lambda x: x.title(), fol)))


class ItemIterator(BaseModel):
    current: str
    next: str = ""
    _host: str = PrivateAttr()
    _get_fn: Callable = PrivateAttr()

    def set_accessor(self, host, get_fn):
        self._host = host
        self._get_fn = get_fn

    def get_next(self):
        """get next paged response"""
        if not self.next:
            return None
        response = self._get_fn(self._host + self.next)
        if response.ok:
            items = parse_raw_as(GetItemsPagedResponse, response.content)
            if items.links.next:
                items.links.set_accessor(self._host, self._get_fn)
            return items


class GetItemsPagedResponse(BaseModel):
    links: ItemIterator = None
    items: List[DatasetItem]

    def __iter__(self):
        yield from self.items
        if self.links:
            next_ = self.links.get_next()
            if next_:
                yield from next_


def get_items(host, dataset=None, item_id=None, filter: dict = None, get_fn: Callable = None, **kwargs):
    """get items API on platform"""
    if get_fn is None:
        get_fn = requests.get

    dataset_id = getattr(dataset, "id", dataset)
    if dataset_id and not item_id and not filter:
        r = get_fn(f"{host}/api/data/{dataset_id}/items", **kwargs)
        return parse_raw_as(List[DatasetItem], r.content)
    elif dataset_id and item_id and not filter:
        r = get_fn(f"{host}/api/data/{dataset_id}/items/{item_id}", **kwargs)
        return parse_raw_as(DatasetItem, r.content)
    else:
        filter = filter or {}
        if dataset_id:
            filter["datasetId"] = dataset_id
        if item_id:
            filter["itemId"] = item_id

        if filter:
            filter = {_to_camel(k): v for k, v in filter.items()}
            kwargs.setdefault("params", {}).update(filter)

        r = get_fn(f"{host}/api/items", **kwargs)
        items = parse_raw_as(GetItemsPagedResponse, r.content)
        items.links.set_accessor(host, get_fn)
        return items


def get_object(host, bici_reference, get_fn=None, **kwargs):
    """get objects API on the platform"""
    if get_fn is None:
        get_fn = requests.get
    r = get_fn(f"{host}/api/objects", params={"biciReference": bici_reference}, **kwargs)
    return parse_raw_as(List[DatasetObject], r.content)


def put_item(host, item, put_fn=None, **kwargs):
    if put_fn is None:
        put_fn = requests.put
    payload = item.dict(by_alias=True, exclude={"dataset_id", "item_id"})
    r = put_fn(f"{host}/api/data/{item.dataset_id}/items/{item.item_id}", **kwargs, json=payload)
    r.raise_for_status()
    if r.status_code == 204:
        return None
    else:
        return parse_raw_as(DatasetItem, r.content)


def delete_item(host, dataset_id, item_id, delete_fn=None, **kwargs):
    if delete_fn is None:
        delete_fn = requests.delete
    r = delete_fn(f"{host}/api/data/{dataset_id}/items/{item_id}", **kwargs)
