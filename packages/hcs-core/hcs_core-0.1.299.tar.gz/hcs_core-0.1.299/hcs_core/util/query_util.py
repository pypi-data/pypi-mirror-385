"""
Copyright 2023-2023 VMware Inc.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Any, Callable, Iterator, Tuple
from urllib.parse import urlencode


def _remove_none(obj: dict):
    keys = list(obj.keys())
    for k in keys:
        v = obj[k]
        if v is None:
            del obj[k]
    return obj


def with_query(url: str, **kwargs: Any) -> str:
    qs = urlencode(_remove_none(dict(kwargs)))
    if qs:
        if url.find("?") < 0:
            url += "?"
        else:
            url += "&"
        url += qs
    return url


class PageRequest:
    def __init__(self, fn_get_page: Callable, fn_filter: Callable = None, **kwargs):
        limit = kwargs.get("limit")
        self.limit = int(limit) if limit else 10
        self.fn_get_page = fn_get_page
        self.fn_filter = fn_filter
        self.query = _remove_none(dict(kwargs))
        if int(self.query.get("size", 0)) < 1:
            self.query["size"] = 20

    def get_page(self, page: int, size: int) -> list:
        content, _ = self.get_page(page, size)
        return content

    def _get_page(self, page: int, size: int) -> Tuple[list, bool]:
        params = dict(self.query)
        params["page"] = page
        params["size"] = size

        query_string = urlencode(params)
        page = self.fn_get_page(query_string)
        if not page or not page.content:
            return [], False
        if self.fn_filter:
            return list(filter(self.fn_filter, page.content)), True
        return page.content, True

    def get(self) -> list:
        ret = []
        page_index = self.query.get("page")
        if page_index is None:
            page_index = 0

        while True:
            self.query["page"] = page_index

            query_string = urlencode(self.query)
            page = self.fn_get_page(query_string)
            if not page or not page.content:
                break

            if self.fn_filter:
                content = list(filter(self.fn_filter, page.content))
            else:
                content = page.content
            ret += content
            if len(ret) > self.limit:
                ret = ret[: self.limit]
                break
            if len(page.content) < self.query["size"]:
                break  # no more items
            page_index += 1

        return ret

    def items(self) -> Iterator:
        page = 0
        size = self.query["size"]

        while True:
            data, has_next = self._get_page(page, size)
            if not has_next:
                break
            for item in data:
                yield item
            page += 1
