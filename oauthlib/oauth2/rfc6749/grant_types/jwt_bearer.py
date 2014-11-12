# -*- coding: utf-8 -*-
"""
oauthlib.oauth2.rfc6749.grant_types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from __future__ import unicode_literals, absolute_import

import json
import logging

from .base import GrantTypeBase
from .. import errors
from ..request_validator import RequestValidator

log = logging.getLogger(__name__)


class JWTBearerTokenGrant(GrantTypeBase):

    """`JWT Bearer Token Grant`_

    .. _`JWT Bearer Token Grant`: https://tools.ietf.org/html/draft-ietf-oauth-jwt-bearer-11
    """

    grant_types = ['urn:ietf:params:oauth:grant-type:jwt-bearer']
    mandatory_parameters = ['grant_type', 'assertion']
    disallowed_duplicates = ['grant_type', 'scope', 'assertion']
    refresh_token = False

    def validate_token_request(self, request):
        self.early_validate_token_request(request)
        self.authenticate_client(request)

        # TODO: Validate Bearer token assertion

        self.late_validate_token_request(request)
