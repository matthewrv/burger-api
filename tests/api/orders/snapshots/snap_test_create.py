# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_create_order_happy_path 1"] = {
    "orders": [],
    "total": 0,
    "totalToday": 0,
}

snapshots["test_create_order_happy_path 2"] = {
    "order": {"id": "da6d00b6-c692-4fa9-8624-479a13c30c7f", "number": 0}
}

snapshots["test_create_order_happy_path 3"] = {
    "orders": [
        {
            "_id": "da6d00b6-c692-4fa9-8624-479a13c30c7f",
            "createdAt": "2025-04-21T10:50:49.105731Z",
            "ingredients": [
                "2d75d3fa-bf09-450a-bcb6-5067648b01e8",
                "0c46c950-ef05-41a4-ba2b-d3224bfd4e2e",
                "f8ceba02-7bf4-484b-9df0-f527134fdc83",
                "2d75d3fa-bf09-450a-bcb6-5067648b01e8",
            ],
            "name": "Тестовый бургер",
            "number": 0,
            "status": "pending",
        }
    ],
    "total": 1,
    "totalToday": 1,
}
