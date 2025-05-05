# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_list_order_reset_today_count 1"] = {
    "orders": [
        {
            "_id": "5296181d-ea21-4dfe-a8b5-c99561fc00f8",
            "createdAt": "2025-04-21T23:59:59.505731Z",
            "ingredients": [
                "2d75d3fa-bf09-450a-bcb6-5067648b01e8",
                "0c46c950-ef05-41a4-ba2b-d3224bfd4e2e",
                "f8ceba02-7bf4-484b-9df0-f527134fdc83",
            ],
            "name": "test order",
            "number": 1234,
            "status": "pending",
        }
    ],
    "total": 1,
    "totalToday": 1,
}

snapshots["test_list_order_reset_today_count 2"] = {
    "orders": [
        {
            "_id": "5296181d-ea21-4dfe-a8b5-c99561fc00f8",
            "createdAt": "2025-04-21T23:59:59.505731Z",
            "ingredients": [
                "2d75d3fa-bf09-450a-bcb6-5067648b01e8",
                "0c46c950-ef05-41a4-ba2b-d3224bfd4e2e",
                "f8ceba02-7bf4-484b-9df0-f527134fdc83",
            ],
            "name": "test order",
            "number": 1234,
            "status": "pending",
        }
    ],
    "total": 1,
    "totalToday": 0,
}
