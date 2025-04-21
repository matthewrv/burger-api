# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_ingredients_list 1"] = {
    "data": [
        {
            "_id": "cae4fd2b-43d4-4e2d-9181-640c1e165ccd",
            "calories": 300,
            "carbohydrates": 20,
            "fat": 10,
            "image": "https://example.com",
            "image_large": "https://example.com",
            "image_mobile": "https://m.example.com",
            "name": "test",
            "price": 255,
            "proteins": 10,
            "type": "bun",
        }
    ],
    "success": True,
}
