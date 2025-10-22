from .return_class import AbstractApiClass


class OrganizationGroup(AbstractApiClass):
    """
        An Organization Group. Defines the permissions available to the users who are members of the group.

        Args:
            client (ApiClient): An authenticated API Client instance
            organizationGroupId (str): The unique identifier of the Organization Group.
            permissions (list of enum string): The list of permissions (VIEW, MODIFY, ADMIN, BILLING, API_KEY, INVITE_USER) the group has.
            groupName (str): The name of the Organization Group.
            defaultGroup (bool): If true, all new users will be added to this group automatically.
            admin (bool): If true, this group contains all permissions available to the organization and cannot be modified or deleted.
            createdAt (str): When the Organization Group was created.
    """

    def __init__(self, client, organizationGroupId=None, permissions=None, groupName=None, defaultGroup=None, admin=None, createdAt=None):
        super().__init__(client, organizationGroupId)
        self.organization_group_id = organizationGroupId
        self.permissions = permissions
        self.group_name = groupName
        self.default_group = defaultGroup
        self.admin = admin
        self.created_at = createdAt
        self.deprecated_keys = {}

    def __repr__(self):
        repr_dict = {f'organization_group_id': repr(self.organization_group_id), f'permissions': repr(self.permissions), f'group_name': repr(
            self.group_name), f'default_group': repr(self.default_group), f'admin': repr(self.admin), f'created_at': repr(self.created_at)}
        class_name = "OrganizationGroup"
        repr_str = ',\n  '.join([f'{key}={value}' for key, value in repr_dict.items(
        ) if getattr(self, key, None) is not None and key not in self.deprecated_keys])
        return f"{class_name}({repr_str})"

    def to_dict(self):
        """
        Get a dict representation of the parameters in this class

        Returns:
            dict: The dict value representation of the class parameters
        """
        resp = {'organization_group_id': self.organization_group_id, 'permissions': self.permissions,
                'group_name': self.group_name, 'default_group': self.default_group, 'admin': self.admin, 'created_at': self.created_at}
        return {key: value for key, value in resp.items() if value is not None and key not in self.deprecated_keys}

    def refresh(self):
        """
        Calls describe and refreshes the current object's fields

        Returns:
            OrganizationGroup: The current object
        """
        self.__dict__.update(self.describe().__dict__)
        return self

    def describe(self):
        """
        Returns the specific organization group passed in by the user.

        Args:
            organization_group_id (str): The unique identifier of the organization group to be described.

        Returns:
            OrganizationGroup: Information about a specific organization group.
        """
        return self.client.describe_organization_group(self.organization_group_id)

    def add_permission(self, permission: str):
        """
        Adds a permission to the specified Organization Group.

        Args:
            permission (str): Permission to add to the Organization Group.
        """
        return self.client.add_organization_group_permission(self.organization_group_id, permission)

    def remove_permission(self, permission: str):
        """
        Removes a permission from the specified Organization Group.

        Args:
            permission (str): The permission to remove from the Organization Group.
        """
        return self.client.remove_organization_group_permission(self.organization_group_id, permission)

    def delete(self):
        """
        Deletes the specified Organization Group

        Args:
            organization_group_id (str): Unique string identifier of the organization group.
        """
        return self.client.delete_organization_group(self.organization_group_id)

    def add_user_to(self, email: str):
        """
        Adds a user to the specified Organization Group.

        Args:
            email (str): Email of the user to be added to the group.
        """
        return self.client.add_user_to_organization_group(self.organization_group_id, email)

    def remove_user_from(self, email: str):
        """
        Removes a user from an Organization Group.

        Args:
            email (str): Email of the user to remove.
        """
        return self.client.remove_user_from_organization_group(self.organization_group_id, email)

    def set_default(self):
        """
        Sets the default Organization Group to which all new users joining an organization are automatically added.

        Args:
            organization_group_id (str): Unique string identifier of the Organization Group.
        """
        return self.client.set_default_organization_group(self.organization_group_id)
