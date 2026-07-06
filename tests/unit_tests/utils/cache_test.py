# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# pylint: disable=import-outside-toplevel, unused-argument

import re

from pytest_mock import MockerFixture


def test_memoized_func(mocker: MockerFixture) -> None:
    """
    Test the ``memoized_func`` decorator.
    """
    from superset.utils.cache import memoized_func

    cache = mocker.MagicMock()

    decorator = memoized_func("db:{self.id}:schema:{schema}:view_list", cache)
    decorated = decorator(lambda self, schema, cache=False: 42)

    self = mocker.MagicMock()
    self.id = 1

    # skip cache
    result = decorated(self, "public", cache=False)
    assert result == 42
    cache.get.assert_not_called()

    # check cache, no cached value
    cache.get.return_value = None
    result = decorated(self, "public", cache=True)
    assert result == 42
    cache.get.assert_called_with("db:1:schema:public:view_list")

    # check cache, cached value
    cache.get.return_value = 43
    result = decorated(self, "public", cache=True)
    assert result == 43


def test_set_and_log_cache_dttm_format(mocker: MockerFixture) -> None:
    """
    The ``dttm`` stored in cached payloads must use the exact
    ``YYYY-MM-DDTHH:MM:SS`` format (no microseconds, no tz offset).
    """
    from superset.utils import cache as cache_module
    from superset.utils.cache import set_and_log_cache

    app = mocker.patch.object(cache_module, "app")
    app.config = {"CACHE_DEFAULT_TIMEOUT": 60, "STATS_LOGGER": mocker.MagicMock()}

    cache_instance = mocker.MagicMock()
    cache_instance.cache = mocker.MagicMock()

    set_and_log_cache(cache_instance, "some_key", {"foo": "bar"})

    cache_instance.set.assert_called_once()
    stored_value = cache_instance.set.call_args.args[1]
    dttm = stored_value["dttm"]
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", dttm), dttm
