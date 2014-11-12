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


class ClientCredentialsGrant(GrantTypeBase):

    """`Client Credentials Grant`_

    The client can request an access token using only its client
    credentials (or other supported means of authentication) when the
    client is requesting access to the protected resources under its
    control, or those of another resource owner that have been previously
    arranged with the authorization server (the method of which is beyond
    the scope of this specification).

    The client credentials grant type MUST only be used by confidential
    clients::

        +---------+                                  +---------------+
        :         :                                  :               :
        :         :>-- A - Client Authentication --->: Authorization :
        : Client  :                                  :     Server    :
        :         :<-- B ---- Access Token ---------<:               :
        :         :                                  :               :
        +---------+                                  +---------------+

    Figure 6: Client Credentials Flow

    The flow illustrated in Figure 6 includes the following steps:

    (A)  The client authenticates with the authorization server and
            requests an access token from the token endpoint.

    (B)  The authorization server authenticates the client, and if valid,
            issues an access token.

    .. _`Client Credentials Grant`: http://tools.ietf.org/html/rfc6749#section-4.4
    """

    grant_types = ['client_credentials']
    mandatory_parameters = ['grant_type']
    disallowed_duplicates = ['grant_type', 'scope']
    refresh_token = False

    def validate_token_request(self, request):
        self.early_validate_token_request(request)
        self.authenticate_client(request)
        self.late_validate_token_request(request)
