from banal import ensure_list

from aleph.core import db, settings
from aleph.model import Collection, Role, Permission


class Authz(object):
    """Hold the authorization information for a user.

    This is usually attached to a request, but can also be used separately,
    e.g. in the context of notifications.
    """
    READ = 'read'
    WRITE = 'write'

    def __init__(self, role_id, roles, is_admin=False, role=None):
        self._cache = {}
        self.id = role_id
        self._role = role
        self.logged_in = role_id is not None
        self.roles = set(roles)
        self.is_admin = is_admin
        self.in_maintenance = settings.MAINTENANCE
        self.session_write = not self.in_maintenance and self.logged_in

    @classmethod
    def from_role(cls, role):
        roles = set([Role.load_id(Role.SYSTEM_GUEST)])
        if role is None:
            return cls(None, roles)

        roles.add(role.id)
        roles.add(Role.load_id(Role.SYSTEM_USER))
        roles.update([g.id for g in role.roles])
        return cls(role.id, roles, is_admin=role.is_admin, role=role)

    def can(self, collection, action):
        """Query permissions to see if the user can perform the specified
        action on the given collection."""
        if action == self.WRITE and not self.session_write:
            return False
        if self.is_admin:
            return True

        if isinstance(collection, Collection):
            collection = collection.id
        if collection is None:
            return False

        # TBD, Should we cache beyond a single request life cycle?
        # probably a horrible idea.
        key = (collection, action)
        if key in self._cache:
            return self._cache[key]

        q = db.session.query(Permission.id)
        q = q.filter(Permission.deleted_at == None)  # noqa
        q = q.filter(Permission.role_id.in_(self.roles))
        q = q.filter(Permission.collection_id == int(collection))
        if action == self.READ:
            q = q.filter(Permission.read == True)  # noqa
        if action == self.WRITE:
            q = q.filter(Permission.write == True)  # noqa
        perm = q.count() > 0
        self._cache[key] = perm
        return perm

    def can_write(self, collection):
        """Check if a given collection can be written."""
        return self.can(collection, self.WRITE)

    def can_read(self, collection):
        """Check if a given collection can be read."""
        return self.can(collection, self.READ)

    def match(self, roles):
        """See if there's overlap in roles."""
        roles = ensure_list(roles)
        if not len(roles):
            return False
        return self.roles.intersection(roles) > 0

    def __repr__(self):
        return '<Authz(%s)>' % self.id
