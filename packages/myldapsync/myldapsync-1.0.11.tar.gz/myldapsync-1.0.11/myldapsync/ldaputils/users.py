###############################################################################
#
# myldapsync - adopted for MySQL fork of pgldapsync by EnterpriseDB Corporation
#
# Synchronise MySQL users with users in an LDAP directory.
#
###############################################################################

"""LDAP user functions."""

import sys

from ldap3.core.exceptions import LDAPInvalidFilterError, \
    LDAPInvalidScopeError, LDAPAttributeError


def get_ldap_users(config, conn, admin):
    """Get a list of users from the LDAP server.

    Args:
        config (ConfigParser): The application configuration
        conn (ldap3.core.connection.Connection): The LDAP connection object
        admin (bool): Return users in the admin group?
    Returns:
        str[]: A list of user names
    """
    users = []

    if admin:
        base_dn = config.get('ldap', 'admin_base_dn')
        search_filter = config.get('ldap', 'admin_filter_string')
    else:
        base_dn = config.get('ldap', 'base_dn')
        search_filter = config.get('ldap', 'filter_string')

    try:
        conn.search(base_dn,
                    search_filter,
                    config.get('ldap', 'search_scope'),
                    attributes=[config.get('ldap', 'username_attribute')]
                          )
    except LDAPInvalidScopeError as exception:
        sys.stderr.write(f"Error searching the LDAP directory: {exception}\n")
        sys.exit(1)
    except LDAPAttributeError as exception:
        sys.stderr.write(f"Error searching the LDAP directory: {exception}\n")
        sys.exit(1)
    except LDAPInvalidFilterError as exception:
        sys.stderr.write(f"Error searching the LDAP directory: {exception}\n")
        sys.exit(1)

    for entry in conn.entries:
        users.append(entry[config.get('ldap', 'username_attribute')].value)

    return users


def get_filtered_ldap_users(config, conn, admin):
    """Get a filtered list of users from the LDAP server, having removed users
    to be ignored.

    Args:
        config (ConfigParser): The application configuration
        conn (ldap3.core.connection.Connection): The LDAP connection object
        admin (bool): Return users in the admin group?
    Returns:
        str[]: A filtered list of user names
    """
    if (users := get_ldap_users(config, conn, admin)) is None:
        return None

    # Remove ignored users
    for user in config.get('ldap', 'ignore_users').split(','):
        try:
            users.remove(user)
        except ValueError:
            pass

    return users
