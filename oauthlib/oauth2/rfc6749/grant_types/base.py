# -*- coding: utf-8 -*-
"""
oauthlib.oauth2.rfc6749.grant_types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from __future__ import unicode_literals, absolute_import

import json
import logging

from oauthlib.oauth2.rfc6749 import errors, utils

log = logging.getLogger(__name__)


class GrantTypeBase(object):
    error_uri = None
    request_validator = None

    mandatory_parameters = ['grant_type']
    disallowed_duplicates = ['grant_type']
    refresh_token = False

    def create_authorization_response(self, request, token_handler):
        raise NotImplementedError('Subclasses must implement this method.')

    def __init__(self, request_validator=None, refresh_token=None):
        self.request_validator = request_validator or RequestValidator()
        if refresh_token is not None:
            self.refresh_token = refresh_token

    def create_token_response(self, request, token_handler):
        """Return token or error in JSON format.

        If the access token request is valid and authorized, the
        authorization server issues an access token as described in
        `Section 5.1`_.  A refresh token SHOULD NOT be included.  If the request
        failed client authentication or is invalid, the authorization server
        returns an error response as described in `Section 5.2`_.

        .. _`Section 5.1`: http://tools.ietf.org/html/rfc6749#section-5.1
        .. _`Section 5.2`: http://tools.ietf.org/html/rfc6749#section-5.2
        """
        headers = {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-store',
            'Pragma': 'no-cache',
        }
        try:
            log.debug('Validating access token request, %r.', request)
            self.validate_token_request(request)
        except errors.OAuth2Error as e:
            log.debug('Client error in token request. %s.', e)
            return headers, e.json, e.status_code

        token = token_handler.create_token(
                request, refresh_token=self.refresh_token)
        log.debug('Issuing token to client id %r (%r), %r.',
                  request.client_id, request.client, token)
        return headers, json.dumps(token), 200

    def early_validate_token_request(self, request):
        for attr in self.mandatory_parameters:
            if not getattr(request, attr):
                raise errors.InvalidRequestError(
                        'Request is missing parameter %s.' % attr,
                        request=request
                )

        if request.grant_type not in self.grant_types:
            raise errors.UnsupportedGrantTypeError(request=request)

        for param in self.disallowed_duplicates:
            if param in request.duplicate_params:
                raise errors.InvalidRequestError(description='Duplicate %s parameter.' % param,
                                                 request=request)

    def late_validate_token_request(self, request):
        # Ensure client is authorized use of this grant type
        self.validate_grant_type(request)
        self.validate_scopes(request)
        request.client_id = request.client_id or request.client.client_id
        log.debug('Setting client_id to %s.', request.client_id)
        log.debug('Authorizing access to user %r.', request.user)

    def validate_grant_type(self, request):
        if not self.request_validator.validate_grant_type(request.client_id,
                                                          request.grant_type, request.client, request):
            log.debug('Unauthorized from %r (%r) access to grant type %s.',
                      request.client_id, request.client, request.grant_type)
            raise errors.UnauthorizedClientError(request=request)

    def validate_scopes(self, request):
        if not request.scopes:
            request.scopes = utils.scope_to_list(request.scope) or utils.scope_to_list(
                self.request_validator.get_default_scopes(request.client_id, request))
        log.debug('Validating access to scopes %r for client %r (%r).',
                  request.scopes, request.client_id, request.client)
        if not self.request_validator.validate_scopes(request.client_id,
                                                      request.scopes, request.client, request):
            raise errors.InvalidScopeError(request=request)


    def authenticate_client(self, request):
        log.debug('Authenticating client, %r.', request)
        if not self.request_validator.authenticate_client(request):
            log.debug('Client authentication failed, %r.', request)
            raise errors.InvalidClientError(request=request)
        else:
            if not hasattr(request.client, 'client_id'):
                raise NotImplementedError('Authenticate client must set the '
                                          'request.client.client_id attribute '
                                          'in authenticate_client.')
