# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 CERN.
# Copyright (C) 2023-2024 Graz University of Technology.
# Copyright (C) 2025 KTH Royal Institute of Technology.
#
# Invenio-Notifications is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio module for notifications support."""

from .ext import InvenioNotifications
from .proxies import current_notifications, current_notifications_manager

__version__ = "1.2.2"

__all__ = (
    "__version__",
    "current_notifications",
    "current_notifications_manager",
    "InvenioNotifications",
)
