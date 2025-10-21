import uuid
from abc import ABC

from typing import List, Tuple, Optional, Set
from netaddr import IPAddress

from cyst.api.configuration.logic.access import AccessLevel
from cyst.api.logic.access import Authorization, AuthenticationToken, AuthenticationTokenSecurity, \
    AuthenticationTokenType, AuthenticationProvider, AuthenticationTarget, AuthenticationProviderType, AccessScheme
from cyst.api.logic.data import Data

from cyst.platform.logic.data import DataImpl


class AuthorizationImpl(Authorization):
    def __init__(self, identity: str = "", nodes: List[str] = None, services: List[str] = None,
                 access_level: AccessLevel = AccessLevel.NONE, id: Optional[str] = None, token: Optional[str] = None):
        if services is None or not services:
            services = ["*"]
        if nodes is None or not nodes:
            nodes = ["*"]
        self._id = id
        self._identity = identity
        self._nodes = nodes
        self._services = services
        self._access_level = access_level
        self._token = token
        self._expiration = -1  # TODO

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AuthorizationImpl):
            return NotImplemented
        if not other:
            return False

        other = AuthorizationImpl.cast_from(other)
        return self.id == other.id or (
                self.identity == other.identity and
                self.nodes == other.nodes and
                self.services == other.services and
                self.access_level == other.access_level and
                self.token == other.token
        )

    @property
    def id(self) -> str:
        #MYPY: complains about optionality of the id, it is also noted, that it is suspicious in Authorization class
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @property
    def identity(self) -> str:
        return self._identity

    @identity.setter
    def identity(self, value: str) -> None:
        self._identity = value

    @property
    def nodes(self) -> List[str]:
        return self._nodes

    @nodes.setter
    def nodes(self, value: List[str]) -> None:
        self._nodes = value

    @property
    def services(self) -> List[str]:
        return self._services

    @services.setter
    def services(self, value: List[str]) -> None:
        self._services = value

    @property
    def access_level(self) -> AccessLevel:
        return self._access_level

    @access_level.setter
    def access_level(self, value: AccessLevel) -> None:
        self._access_level = value

    @property
    def token(self) -> Optional[uuid.UUID]:
        return self._token #MYPY: Authorization has token as not null, however there are calls to this implementation, that do not set it and therefore it can be null. Is relaxing authorization by making token null the correct choice?
    #Also UUID and str is not unified


    @token.setter
    def token(self, value: uuid.UUID) -> None:
        self._token = value #MYPY: uid vs str

    def matching_id(self, other: Authorization):
        return self.id == AuthorizationImpl.cast_from(other).id

    def __str__(self) -> str:
        return "[Id: {}, Identity: {}, Nodes: {}, Services: {}, Access Level: {}, Token: {}]".format(self.id,
                                                                                                     self.identity,
                                                                                                     self.nodes,
                                                                                                     self.services,
                                                                                                     self.access_level.name,
                                                                                                     self.token)

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def cast_from(o: Authorization) -> 'AuthorizationImpl':
        if isinstance(o, AuthorizationImpl):
            return o
        else:
            raise ValueError("Malformed underlying object passed with the Authorization interface")

    @property
    def expiration(self) -> int:
        return self._expiration


class PolicyStats:
    def __init__(self, authorization_entry_count: int = 0):
        self._authorization_entry_count = authorization_entry_count

    @property
    def authorization_entry_count(self):
        return self._authorization_entry_count


# ----------------------------------------------------------------------------------------------------------------------
# New version
# ----------------------------------------------------------------------------------------------------------------------

class AuthenticationTokenImpl(AuthenticationToken):

    def __init__(self, token_type: AuthenticationTokenType, security: AuthenticationTokenSecurity, identity: str,
                 is_local: bool):
        self._type = token_type
        self._security = security
        self._identity = identity
        self._is_local = is_local

        # create data according to the security
        # TODO: Until the concept of sealed data is introduced in the code, all is assumed to be OPEN
        value = uuid.uuid4()
        self._content = None

    @property
    def type(self) -> AuthenticationTokenType:
        return self._type

    @property
    def is_local(self):
        return self._is_local

    @property
    def security(self) -> AuthenticationTokenSecurity:
        return self._security

    @property
    def identity(self) -> str:
        return self._identity #MYPY: Setter is defined in AuthenticationToken, is it OK to add here? It should be here as well

    def copy(self) -> Optional[AuthenticationToken]:
        pass # TODO different uuid needed????

    @property
    def content(self) -> Optional[Data]:
        return self._content

    @staticmethod
    def is_local_instance(obj: AuthenticationToken):
        if isinstance(obj, AuthenticationTokenImpl):
            return obj.is_local
        return False

    def _set_content(self, value) -> 'AuthenticationToken':
        # this is only needed until we resolve hashed/encrypted data
        self._content = DataImpl("", value)
        return self  # just so we can chain call with constructor



class AuthenticationTargetImpl(AuthenticationTarget):
    def __init__(self, tokens: List[AuthenticationTokenType], service: Optional[str] = None,
                 ip: Optional[IPAddress] = None):
        self._address = ip
        self._service = service
        self._tokens = tokens

    @property
    def address(self) -> Optional[IPAddress]:
        return self._address

    @address.setter
    def address(self, ip: IPAddress):
        self._address = ip

    @property
    def service(self) -> str:
        return self._service #MYPY: Service is defined as not optional in AuthenticationTarget, but constructor of impl has it optional and is called in that way

    @service.setter
    def service(self, serv: str):
        self._service = serv

    @property
    def tokens(self) -> List[AuthenticationTokenType]:
        return self._tokens



class AccessSchemeImpl(AccessScheme):
    def __init__(self, id: str):
        self._providers = []
        self._authorizations: List[Authorization] = []
        self._identities: List[str] = []
        self._id = id

    def add_provider(self, provider: AuthenticationProvider):
        self._providers.append((provider, len(self._providers)))

    def add_identity(self, identity: str):
        self._identities.append(identity)

    def add_authorization(self, auth: Authorization):
        self._authorizations.append(auth)

    def remove_authorization(self, auth: Authorization):
        # removing authorization means setting access level to NONE
        auth.access_level = AccessLevel.NONE

    def register_authorization(self, auth: Authorization) -> None:
        identity = AuthorizationImpl.cast_from(auth).identity
        if identity not in self.identities:
            self.add_identity(identity)
        self.add_authorization(auth)

    def is_local(self) -> bool:
        return all(p.type is AuthenticationProviderType.LOCAL for p, _ in self.factors)

    def match_tokens(self, tokens: List[AuthenticationToken]) -> bool:
        return len(tokens) == len(self.factors) and \
                all(AuthenticationProviderImpl.cast_from(factor).is_token_matching(token)
                    for (factor, _), token in zip(self.factors, tokens))

    def create_access(self, identity: str, access_level: AccessLevel, tokens: List[AuthenticationToken]) -> List[AuthenticationToken]:
        self.register_authorization(AuthorizationImpl(identity, id=str(uuid.uuid4()), access_level=access_level))

        # no tokens supplied, create and return new ones
        if not tokens:
            return [AuthenticationProviderImpl.cast_from(p).register_new_token(identity) for p, _ in self.factors]

        # otherwise add tokens to each factor one by one
        for (factor, _), token in zip(self.factors, tokens):
            AuthenticationProviderImpl.cast_from(factor).add_token(token)

        return tokens

    def modify_access(self, identity: str, access_level: AccessLevel) -> None:
        # WARN: this will raise exception if identity not present
        template = next(a for a in self.authorizations if a.identity == identity)
        AuthorizationImpl.cast_from(template).access_level = access_level

    @property
    def factors(self) -> List[Tuple[AuthenticationProvider, int]]:
        return self._providers
    # TODO : what is the number?? I will just use order ATM

    @property
    def identities(self) -> List[str]:
        return self._identities

    @property
    def authorizations(self) -> List[Authorization]:
        return self._authorizations

    @property
    def id(self) -> str:
        return self._id

    @staticmethod
    def cast_from(other: AccessScheme):
        if isinstance(other, AccessSchemeImpl):
            return other
        else:
            raise ValueError("Malformed underlying object passed with the AccessScheme interface")


class AuthenticationProviderImpl(AuthenticationProvider):

    class AuthenticationTokenState(ABC):
        def __init__(self, token: AuthenticationToken):
            self._token = token
            self._enabled = True
            self._disabled_until = 0

        @property
        def token(self) -> AuthenticationToken:
            return self._token

        @property
        def enabled(self) -> bool:
            return self._enabled

        def enable_token(self) -> None:
            self._enabled = True
            self._disabled_until = 0

        def disable_token(self, time: int) -> None:
            self._enabled = False
            self._disabled_until = time

        def is_token_valid(self, time: int) -> bool:
            if self._disabled_until < time:
                # if _disabled_until expired, token is active at the time 'time', therefore enable token
                self.enable_token()
            return self._enabled

    def __init__(self, provider_type: AuthenticationProviderType, token_type: AuthenticationTokenType,
                 security: AuthenticationTokenSecurity, ip: Optional[IPAddress], timeout: int, id: str):

        self._provider_type = provider_type
        self._token_type = token_type
        self._security = security
        self._timeout = timeout

        self._tokens: Set[AuthenticationToken] = set()
        self._target = self._create_target()

        self._id = id

        if provider_type != AuthenticationProviderType.LOCAL and ip is None:
            raise RuntimeError("Non-local provider needs ip address")
        self._set_address(ip)

    @property
    def type(self) -> AuthenticationProviderType:
        return self._provider_type

    @property
    def target(self) -> AuthenticationTarget:
        return self._target

    @property
    def token_type(self):
        return self._token_type

    @property
    def security(self):
        return self._security

    @property
    def id(self) -> str:
        return self._id

    def token_is_registered(self, token: AuthenticationToken):
        for token_state in set(self._tokens):
            if token_state.token.identity == token.identity and token.content is not None:
                # This is pretty weak but until encrypted/hashed stuff is implemented its okay for testing
                return True
        return False

    def create_token(self, identity: str) -> AuthenticationToken:
        return AuthenticationTokenImpl(self._token_type, self._security, identity,
                self._provider_type is AuthenticationProviderType.LOCAL)._set_content(uuid.uuid4())

    def register_new_token(self, identity: str) -> AuthenticationToken:
        token = self.create_token(identity)
        self.add_token(token)
        return token

    def is_token_matching(self, token: AuthenticationToken) -> bool:
        return isinstance(token, AuthenticationTokenImpl) and \
            token.security is self.security and \
            token.type is self.token_type and \
            token.is_local == (self.type is AuthenticationProviderType.LOCAL)

    def add_token(self, token: AuthenticationToken):
        self._tokens.add(self.AuthenticationTokenState(token))

    def disable_token(self, token: AuthenticationToken, time: int):
        for token_state in set(self._tokens):
            if token_state.token == token:
                token_state.disable_token(time)

    def enable_token(self, token: AuthenticationToken):
        for token_state in set(self._tokens):
            if token_state.token == token:
                token_state.enable_token()

    def is_token_valid(self, token: AuthenticationToken, time: int) -> bool:
        for token_state in set(self._tokens):
            # TODO: the token is matched only by identity on the premise that one authentication factor has only one
            #       auth token for identity. Evaluate if this is really true or not
            if token_state.token.identity == token.identity:
                return token_state.is_token_valid(time)

    def remove_token_by_identity(self, identity: str):
        for token_state in set(self._tokens):
            if token_state.token.identity == identity:
                self._tokens.remove(token_state)

    def get_token_by_identity(self, identity: str):
        for token_state in set(self._tokens):
            if token_state.token.identity == identity:
                return token_state.token

    def _create_target(self):
        # TODO: inherit from provider? or should we do something else?
        return AuthenticationTargetImpl([self._token_type])

    def set_service(self, srv_id: str):

        if self._target.service is None:
            self._target.service = srv_id
        # Due to the way a configuration works from version 0.6.0, the same service can be set multiple times. So we
        # just ignore it.
        elif self._target.service == srv_id:
            pass
        else:
            raise RuntimeError  # TODO check what should be done here, exception might be too harsh

    def _set_address(self, ip: IPAddress):
        if self._target.address is None:
            self._target.address = ip
        else:
            raise RuntimeError

    @staticmethod
    def cast_from(other: AuthenticationProvider):
        if isinstance(other, AuthenticationProviderImpl):
            return other
        else:
            raise ValueError("Malformed underlying object passed with the AuthenticationProvider interface")
