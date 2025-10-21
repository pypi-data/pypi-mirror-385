from dataclasses import dataclass, field
from flags import Flags
from typing import Optional, Dict, Any, List, Union, Tuple
from uuid import uuid4

from serde import serialize, coerce

from cyst.api.configuration.configuration import ConfigItem
from cyst.api.configuration.logic.access import AuthorizationConfig, AccessSchemeConfig, AuthenticationProviderConfig, AuthenticationTokenConfig
from cyst.api.configuration.logic.data import DataConfig

from cyst.api.logic.access import AccessLevel


class ServiceParameter(Flags):
    """
    Service parameter represents a domain of parametrization for passive services.

    Values
        :ENABLE_SESSION: A service can be a destination of a session, e.g., SSH or VPN tunnel, or HTTP server.
            Possible values: True|False
        :SESSION_ACCESS_LEVEL: An access level of a session when it is established. This can be different from the
            service access level, e.g., SSH daemon has an elevated service access level, but its sessions are always
            limited. Possible values: the domain of cyst.api.logic.access.AccessLevel.
    """
    ENABLE_SESSION = ()
    SESSION_ACCESS_LEVEL = ()


@serialize(type_check=coerce)
@dataclass
class ActiveServiceConfig(ConfigItem):
    """ A configuration for an Active service.

    :param type: A unique name of service type, with which it is registered into the system.
    :type type: str

    :param name: A unique name of service on a given node.

        This name currently equals to a port identification, but in future releases a service will have a list of opened
        ports.
    :type name: str

    :param owner: An identity of the owner of the service.

        This identity should exist on the node, but it is currently not enforced.
    :type owner: str

    :param access_level: The access level of the service, i.e., the resources the service can access.
    :type access_level: AccessLevel

    :param configuration: A dictionary of any parameters configuring the behavior of the service.

        The configuration is strictly service-dependent and there is no common configuration. For possible values
        consult service documentation.
    :type configuration: Optional[Dict[str, Any]]

    """
    type: str
    name: str
    owner: str
    access_level: AccessLevel
    configuration: Optional[Dict[str, Any]] = None
    id: str = ""
    ref: str = field(default_factory=lambda: str(uuid4()))


@serialize(type_check=coerce)
@dataclass
class PassiveServiceConfig(ConfigItem):
    """ A configuration for a Passive service.

        Any configuration parameter in the form Union[...Config, str] means that the parameter can be specified either
        inline, or can be referenced by its id. This enables a better structuring of a code.

    :param name: A name of the passive service.

        While the name can be anything, and it is not in any way enforced, this name is used to evaluate applicability
        of exploits, so two services susceptible to the same exploit should have the same name.

        This name currently equals to a port identification, but in future releases a service will have a list of opened
        ports.
    :type name: str

    :param owner: An identity of the owner of the service.

        This identity should exist on the node, but it is currently not enforced.
    :type owner: str

    :param version: A version of the service.

        The version specifier should follow semantic versioning scheme. Otherwise unintended consequences will occur.
        The version is also used to evaluate applicability of exploits.
    :type version: str

    :param local: Availability of the service across the network.

        If TRUE, the service does not have associated network port and can't be accessed remotely.
        If FALSe, the service does have a network port with its name associated and can be accessed, provided the
        routing enables it.
    :type local: bool

    :param access_level: The access level of the service.
        If the service is successfully compromised, then this will be the access level that the attacker will be able to
        use.
    :type access_level: AccessLevel

    :param authentication_providers: A set of authentication providers that the service uses.

        Example:

        .. code-block:: python

            local_password_auth = AuthenticationProviderConfig(
                provider_type=AuthenticationProviderType.LOCAL,
                token_type=AuthenticationTokenType.PASSWORD,
                token_security=AuthenticationTokenSecurity.SEALED,
                timeout=30
            )

            c = PassiveServiceConfig(
                ...
                authentication_providers=[local_password_auth("openssh_local_pwd_auth")],
                ...
            )

    :type authentication_providers: List[Optional[Union[AuthenticationProviderConfig, str]]]

    :param access_schemes: A set of schemes for accessing the service.

        An access scheme consists of authentication providers and authorization domains. For the complete logic behind
        authentication and authorization, see developer documentation.

        Example:

        .. code-block:: python

            access_schemes=[AccessSchemeConfig(
                authentication_providers=["openssh_local_pwd_auth"],
                authorization_domain=AuthorizationDomainConfig(
                    type=AuthorizationDomainType.LOCAL,
                    authorizations=[
                        AuthorizationConfig("user1", AccessLevel.LIMITED, id="ssh_auth_1"),
                        AuthorizationConfig("user2", AccessLevel.LIMITED, id="ssh_auth_2"),
                        AuthorizationConfig("root", AccessLevel.ELEVATED)
                    ]
                )
            )]

    :type access_schemes: List[AccessSchemeConfig]

    :param public_data: A set of data, that can be extracted from the service without authorization.
    :type public_data: List[Union[DataConfig, str]]

    :param private_data: A set of data, that can be extracted from the service with authorization.
    :type private_data: List[Union[DataConfig, str]]

    :param public_authorizations: A set of authentications/authorizations that can be extracted from the service without authorization.

        This function is DEPRECATED, because it does not conform to new authentication/authorization framework, but it
        is currently left here, because some tests still depend on it.
    :type public_authorizations: List[Union[AuthorizationConfig, str]]

    :param public_authorizations: A set of authentications/authorizations that can be extracted from the service with authorization.

        This function is DEPRECATED, because it does not conform to new authentication/authorization framework, but it
        is currently left here, because some tests still depend on it.
    :type public_authorizations: List[Union[AuthorizationConfig, str]]

    :param parameters: A set of parameters for the service.

        The parameters can be chosen from the specific domain of ServiceParameter.

        Example:

        .. code-block:: python

            parameters=[
                (ServiceParameter.ENABLE_SESSION, True),
                (ServiceParameter.SESSION_ACCESS_LEVEL, AccessLevel.LIMITED)
            ],

    :type parameters: List[Tuple[ServiceParameter, Any]]
    """
    name: str
    owner: str
    version: str
    local: bool
    access_level: AccessLevel
    authentication_providers: List[Optional[Union[AuthenticationProviderConfig, str]]] = field(default_factory=lambda: [])
    access_schemes: List[AccessSchemeConfig] = field(default_factory=lambda: [])
    public_data: List[Union[DataConfig, str]] = field(default_factory=lambda: [])
    private_data: List[Union[DataConfig, str]] = field(default_factory=lambda: [])
    public_authorizations: List[Union[AuthorizationConfig, AuthenticationTokenConfig, str]] = field(default_factory=lambda: [])
    private_authorizations: List[Union[AuthorizationConfig, AuthenticationTokenConfig, str]] = field(default_factory=lambda: [])
    parameters: List[Tuple[ServiceParameter, Any]] = field(default_factory=lambda: [])
    id: str = ""
    ref: str = field(default_factory=lambda: str(uuid4()))
