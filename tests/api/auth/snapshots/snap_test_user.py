# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_get_user 1"] = {"user": {"email": "test@example.com", "name": "test"}}

snapshots["test_update_user_email_registered 1"] = {
    "detail": {"message": "Email already reserved", "success": False}
}

snapshots["test_update_user_happy_path[email_only] 1"] = {
    "success": True,
    "user": {"email": "test2@example.com", "name": "test"},
}

snapshots["test_update_user_happy_path[name_only] 1"] = {
    "success": True,
    "user": {"email": "test@example.com", "name": "new_name"},
}

snapshots["test_update_user_happy_path[password_only] 1"] = {
    "success": True,
    "user": {"email": "test@example.com", "name": "test"},
}
