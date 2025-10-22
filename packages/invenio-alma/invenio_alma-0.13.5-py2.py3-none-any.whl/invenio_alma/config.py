# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2025 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module to connect InvenioRDM to Alma."""

from collections.abc import Callable

from invenio_records_resources.services.records.results import RecordItem

ALMA_API_KEY = ""
"""Default value for the Alma API key.

The implemenation assumes that with the key it is only allowed to
create records within Institution Zone (IZ). The Network Zone (NZ)
would need higher permissions.

With the IZ key it is only possible to change 98X fields within an
existing record, but it is possible to create a totally new record.

This value should be set on a place which is not under DVCS control.
"""

ALMA_API_HOST: str = ""
"""Default value for the Alma API host.

This value should be set on a place which is not under DVCS control.
"""

ALMA_REPOSITORY_RECORDS_IMPORT_FUNCS: dict[str, Callable[..., RecordItem]] = {}
"""Function to import a record from alma into the repository."""

ALMA_ALMA_RECORDS_CREATE_AGGREGATORS: dict[
    str,
    Callable[..., list[tuple[str, str]]],
] = {}
"""List of aggregators with following signature: aggregator() -> list[marc_id]."""

ALMA_ALMA_RECORDS_CREATE_FUNCS: dict[str, Callable[..., RecordItem]] = {}
"""The function to create record in alma."""

ALMA_REPOSITORY_RECORDS_UPDATE_AGGREGATORS: dict[
    str,
    Callable[..., list[tuple[str, str]]],
] = {}
"""List of aggregators with following signature: aggregator() -> list[tuple[marc_id, alma_id]]."""

ALMA_REPOSITORY_RECORDS_UPDATE_FUNCS: dict[str, Callable[..., RecordItem]] = {}
"""This is a callable to make the update process dependend on the workflow."""

ALMA_USER_EMAIL: str = ""
"""This is the email adress of the alma user in the repository."""

ALMA_ERROR_MAIL_SENDER: str = ""
"""This is the error mail sender."""

ALMA_ERROR_MAIL_RECIPIENTS: list[str] = []
"""This is a list of recipients who should get the error message."""

ALMA_CELERY_BEAT_SCHEDULE: dict = {}
"""Celery beat schedule for the theses import.

This should be set on the InvenioRDM instance invenio.cfg file.
"""

ALMA_SRU_DOMAIN = ""
"""SRU domain.

This is the domain of the institution Alma SRU service.
"""

ALMA_SRU_INSTITUTION_CODE = ""
"""SRU institution code.

This is the code that acts as a reference for the institution in Alma.
"""
