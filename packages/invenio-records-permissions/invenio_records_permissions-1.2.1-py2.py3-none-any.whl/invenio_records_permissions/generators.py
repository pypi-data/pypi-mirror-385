# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2023 CERN.
# Copyright (C) 2019-2020 Northwestern University.
# Copyright (C) 2024 Ubiquity Press.
#
# Invenio-Records-Permissions is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Invenio Records Permissions Generators."""

import operator
from abc import abstractmethod
from functools import reduce
from itertools import chain

from flask import current_app
from flask_principal import ActionNeed, UserNeed
from invenio_access import ActionRoles, ActionUsers, Permission
from invenio_access.permissions import (
    any_user,
    authenticated_user,
    superuser_access,
    system_process,
)
from invenio_search.engine import dsl


class Generator(object):
    """Parent class mapping the context when an action is allowed or denied.

    It does so by *generating* "needed" and "excluded" Needs. At the search
    level it implements the *query filters* to restrict the search.

    Any context inherits from this class.
    """

    def needs(self, **kwargs):
        """Enabling Needs."""
        return []

    def excludes(self, **kwargs):
        """Preventing Needs."""
        return []

    def query_filter(self, **kwargs):
        """Search filters."""
        return []


class AnyUser(Generator):
    """Allows any user."""

    def needs(self, **kwargs):
        """Enabling Needs."""
        return [any_user]

    def query_filter(self, **kwargs):
        """Match all in search."""
        # TODO: Implement with new permissions metadata
        return dsl.Q("match_all")


class SystemProcess(Generator):
    """Allows system_process role."""

    def needs(self, **kwargs):
        """Enabling Needs."""
        return [system_process]

    def query_filter(self, identity=None, **kwargs):
        """Filters for current identity as system process."""
        if system_process in identity.provides:
            return dsl.Q("match_all")
        else:
            return []


class SystemProcessWithoutSuperUser(SystemProcess):
    """Allows system_process role, excluding superuser-access needs."""

    @staticmethod
    def _expand_superuser_access_action():
        """Fetch users and roles allowed for the superuser-access action."""
        roles = (
            ActionRoles.query_by_action(superuser_access).join(ActionRoles.role).all()
        )
        users = ActionUsers.query_by_action(superuser_access).all()
        return chain(roles, users)

    def excludes(self, **kwargs):
        """Preventing Needs."""
        return [role.need for role in self._expand_superuser_access_action()]


class Disable(Generator):
    """Denies ALL users including users and roles allowed to superuser-access action."""

    def excludes(self, **kwargs):
        """Preventing Needs."""
        return [any_user]

    def query_filter(self, **kwargs):
        """Match None in search."""
        return ~dsl.Q("match_all")


class RecordOwners(Generator):
    """Allows record owners."""

    def needs(self, record=None, **kwargs):
        """Enabling Needs."""
        return [UserNeed(owner) for owner in record.get("owners", [])]

    def query_filter(self, identity=None, **kwargs):
        """Filters for current identity as owner."""
        for need in identity.provides:
            if need.method == "id":
                return dsl.Q("term", owners=need.value)
        return []


class AnyUserIfPublic(Generator):
    """Allows any user if record is public.

    TODO: Revisit when dealing with files.
    """

    def needs(self, record=None, **kwargs):
        """Enabling Needs."""
        is_restricted = record and record.get("_access", {}).get(
            "metadata_restricted", False
        )
        return [any_user] if not is_restricted else []

    def excludes(self, record=None, **kwargs):
        """Preventing Needs."""
        return []

    def query_filter(self, **kwargs):
        """Filters for non-restricted records."""
        # TODO: Implement with new permissions metadata
        return dsl.Q("term", **{"_access.metadata_restricted": False})


class AuthenticatedUser(Generator):
    """Allows authenticated users."""

    def needs(self, **kwargs):
        """Enabling Needs."""
        return [authenticated_user]

    def query_filter(self, **kwargs):
        """Filters for current identity as super user."""
        # TODO: Implement with new permissions metadata
        return dsl.Q("match_all")


class AllowedByAccessLevel(Generator):
    """Allows users/roles/groups that have an appropriate access level."""

    # TODO: Implement other access levels:
    # 'metadata_reader'
    # 'files_reader'
    # 'files_curator'
    # 'superuser'
    ACTION_TO_ACCESS_LEVELS = {
        "create": [],
        "read": ["metadata_curator"],
        "update": ["metadata_curator"],
        "delete": [],
    }

    def __init__(self, action="read"):
        """Constructor."""
        self.action = action

    def needs(self, record=None, **kwargs):
        """Enabling UserNeeds for each person."""
        if not record:
            return []

        access_levels = AllowedByAccessLevel.ACTION_TO_ACCESS_LEVELS.get(
            self.action, []
        )

        # Name "identity" is used bc it correlates with flask-principal
        # identity while not being one.
        allowed_identities = chain.from_iterable(
            [
                record.get("internal", {})
                .get("access_levels", {})
                .get(access_level, [])
                for access_level in access_levels
            ]
        )

        return [
            UserNeed(identity.get("id"))
            for identity in allowed_identities
            if identity.get("scheme") == "person" and identity.get("id")
            # TODO: Implement other schemes
        ]

    def query_filter(self, identity=None, **kwargs):
        """Search filter for the current user with this generator."""
        id_need = next(
            (need for need in identity.provides if need.method == "id"), None
        )

        if not id_need:
            return []

        # To get the record in the search results, the access level must
        # have been put in the 'read' array
        read_levels = AllowedByAccessLevel.ACTION_TO_ACCESS_LEVELS.get("read", [])

        queries = [
            dsl.Q(
                "term",
                **{
                    "internal.access_levels.{}".format(access_level): {
                        "scheme": "person",
                        "id": id_need.value,
                        # TODO: Implement other schemes
                    }
                }
            )
            for access_level in read_levels
        ]

        return reduce(operator.or_, queries)


class AdminAction(Generator):
    """Generator for admin needs.

    This generator's purpose is to be used in cases where administration needs are required.
    The query filter of this generator is quite broad (match_all). Therefore, it must be used with care.
    """

    def __init__(self, action):
        """Constructor."""
        self.action = action
        super().__init__()

    def needs(self, **kwargs):
        """Enabling Needs."""
        return [self.action]

    def query_filter(self, identity=None, **kwargs):
        """Not implemented at this level."""
        permission = Permission(self.action)
        if identity and permission.allows(identity):
            return dsl.Q("match_all")
        return []


class ConditionalGenerator(Generator):
    """Generator that depends on whether a condition is true or not.

    .. code-block::python

        If...(
            then_=[...],
            else_=[...],
        )
    """

    def __init__(self, then_, else_):
        """Constructor."""
        self.then_ = then_
        self.else_ = else_

    @abstractmethod
    def _condition(self, **kwargs):
        """Condition to choose generators set."""
        raise NotImplementedError()

    def _generators(self, record, **kwargs):
        """Get the "then" or "else" generators."""
        return self.then_ if self._condition(record=record, **kwargs) else self.else_

    def needs(self, record=None, **kwargs):
        """Set of Needs granting permission."""
        needs = [
            g.needs(record=record, **kwargs) for g in self._generators(record, **kwargs)
        ]
        return set(chain.from_iterable(needs))

    def excludes(self, record=None, **kwargs):
        """Set of Needs denying permission."""
        excludes = [
            g.excludes(record=record, **kwargs)
            for g in self._generators(record, **kwargs)
        ]
        return set(chain.from_iterable(excludes))

    @staticmethod
    def _make_query(generators, **kwargs):
        """Make a query for one set of generators."""
        queries = [g.query_filter(**kwargs) for g in generators]
        queries = [q for q in queries if q]
        return reduce(operator.or_, queries) if queries else None


class IfConfig(ConditionalGenerator):
    """Config-based conditional generator."""

    def __init__(self, config_key, accept_values=None, **kwargs):
        """Initialize generator."""
        self.accept_values = accept_values or [True]
        self.config_key = config_key
        super().__init__(**kwargs)

    def _condition(self, **_):
        """Check if the config value is truthy."""
        return current_app.config.get(self.config_key) in self.accept_values


#
# | Meta Restricted | Files Restricted | Access Right | Result |
# |-----------------|------------------|--------------|--------|
# |       True      |       True       |   Not Open   |  False |
# |-----------------|------------------|--------------|--------|
# |       True      |       True       |     Open     |  False | # Inconsistent
# |-----------------|------------------|--------------|--------|
# |       True      |       False      |   Not Open   |  False | # Inconsistent
# |-----------------|------------------|--------------|--------|
# |       True      |       False      |     Open     |  False | # Inconsistent
# |-----------------|------------------|--------------|--------|
# |       False     |       True       |   Not Open   |  False | ??Inconsistent
# |-----------------|------------------|--------------|--------|
# |       False     |       True       |     Open     |  False |
# |-----------------|------------------|--------------|--------|
# |       False     |       False      |   Not Open   |  False | # Inconsistent
# |-----------------|------------------|--------------|--------|
# |       False     |       False      |     Open     |  True  |
# |-----------------|------------------|--------------|--------|
#
