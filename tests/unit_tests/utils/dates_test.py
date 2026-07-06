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
from datetime import datetime, timedelta, timezone

from freezegun import freeze_time

from superset.utils.dates import datetime_to_epoch, now_as_float


def test_datetime_to_epoch_naive_utc() -> None:
    # A naive datetime is treated as UTC.
    dttm = datetime(1970, 1, 1)
    assert datetime_to_epoch(dttm) == 0.0

    dttm = datetime(1970, 1, 1, 0, 0, 1)
    assert datetime_to_epoch(dttm) == 1000.0


def test_datetime_to_epoch_aware_utc() -> None:
    dttm = datetime(1970, 1, 1, tzinfo=timezone.utc)
    assert datetime_to_epoch(dttm) == 0.0

    dttm = datetime(1970, 1, 1, 0, 0, 1, tzinfo=timezone.utc)
    assert datetime_to_epoch(dttm) == 1000.0


def test_datetime_to_epoch_aware_and_naive_equivalent() -> None:
    naive = datetime(2021, 3, 14, 15, 9, 26)
    aware = naive.replace(tzinfo=timezone.utc)
    assert datetime_to_epoch(aware) == datetime_to_epoch(naive)


def test_datetime_to_epoch_aware_non_utc() -> None:
    # UTC+5:30; the underlying instant equals the epoch, so result is 0.
    ist = timezone(timedelta(hours=5, minutes=30))
    dttm = datetime(1970, 1, 1, 5, 30, tzinfo=ist)
    assert datetime_to_epoch(dttm) == 0.0

    # A non-UTC aware datetime must be converted before diffing.
    dttm = datetime(2021, 3, 14, 20, 39, 26, tzinfo=ist)
    expected = datetime(2021, 3, 14, 15, 9, 26, tzinfo=timezone.utc)
    assert datetime_to_epoch(dttm) == datetime_to_epoch(expected)


def test_datetime_to_epoch_is_milliseconds() -> None:
    # One hour past the epoch is 3_600_000 ms, not 3_600 s.
    dttm = datetime(1970, 1, 1, 1, 0, 0)
    assert datetime_to_epoch(dttm) == 3_600_000.0


def test_now_as_float_frozen_clock() -> None:
    frozen = datetime(2021, 3, 14, 15, 9, 26, tzinfo=timezone.utc)
    with freeze_time(frozen):
        assert now_as_float() == datetime_to_epoch(frozen)
