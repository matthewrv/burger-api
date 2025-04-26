# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_login_happy_path 1"] = {"email": "test@example.com", "name": "test"}

snapshots["test_login_invalid_email 1"] = {"detail": "Incorrect username or password"}

snapshots["test_login_invalid_password 1"] = {
    "detail": "Incorrect username or password"
}
