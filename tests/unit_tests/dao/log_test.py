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
from datetime import datetime, timedelta

import humanize
from freezegun import freeze_time
from pytest_mock import MockerFixture
from sqlalchemy.orm.session import Session

FROZEN_NOW = "2025-01-01 12:00:00"


def test_get_recent_activity_time_delta_naive_dttm(
    mocker: MockerFixture, session: Session
) -> None:
    """
    The humanized ``time_delta`` is computed against a *naive* (UTC) ``dttm``
    without raising ``TypeError`` and stays byte-identical to the legacy
    ``datetime.utcnow() - log.dttm`` output.
    """
    from superset import db
    from superset.daos.log import LogDAO
    from superset.models.core import Log
    from superset.models.dashboard import Dashboard

    Log.metadata.create_all(db.session.get_bind())  # pylint: disable=no-member

    mocker.patch("superset.daos.log.get_user_id", return_value=1)

    with freeze_time(FROZEN_NOW):
        # Stored naive UTC timestamp, two days before "now".
        naive_dttm = datetime(2024, 12, 30, 12, 0, 0)

        dashboard = Dashboard(dashboard_title="my dashboard", slug="my-slug")
        db.session.add(dashboard)
        db.session.flush()

        log = Log(
            action="log",
            user_id=1,
            dashboard_id=dashboard.id,
            json='{"event_name": "mount_dashboard"}',
            dttm=naive_dttm,
        )
        db.session.add(log)
        db.session.flush()

        payload = LogDAO.get_recent_activity(
            actions=["mount_dashboard"],
            distinct=False,
            page=0,
            page_size=100,
        )

        # Legacy behavior: naive utcnow minus a naive dttm.
        expected = humanize.naturaltime(datetime.utcnow() - naive_dttm)

    assert len(payload) == 1
    assert payload[0]["time_delta_humanized"] == expected
    assert payload[0]["time_delta_humanized"] == humanize.naturaltime(timedelta(days=2))
