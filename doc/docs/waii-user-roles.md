---
id: waii-user-roles
title: Waii Roles Overview 
---

Waii implements a hierarchical role-based access control system. Each role builds upon the previous one, inheriting all permissions and adding new ones. Here's an overview of the different roles, from lowest to highest access level:

## 1. Waii Trial User (waii-trial-user)
- The most basic role with limited read-only access.
- Suitable for users trying out the system. (only available for SaaS)

## 2. Waii User (waii-user)
- Builds upon the Trial User role.
- Adds basic write permissions (add database connection, update semantic context for the user itself).
- Appropriate for regular users of the system.

## 3. Waii API User (waii-api-user)
- Extends the Waii User role.
- Includes API usage capabilities.
- Ideal for users who need to interact with the system programmatically.

## 4. Waii Admin User (waii-admin-user)
- Builds upon the API User role.
- Adds publishing capabilities for certain system elements: for example, publishing a semantic context to all the users who have access to the same database connection.
- Suitable for users with administrative responsibilities within their scope.

## 5. Waii Org Admin User (waii-org-admin-user)
- Extends the Admin User role.
- Includes organization-level read and write permissions. (But cannot update the organization itself, or create new organizations)
- Adds user management capabilities and advanced features.
- Appropriate for users managing an entire organization within Waii.

## 6. Waii Super Admin User (waii-super-admin-user)
- The highest level role, building upon the Org Admin User.
- Adds system-wide organizational read and write permissions.
- Suitable for system-wide administrators with the highest level of access.

## Examples 

Waii roles are defined inside the `WaiiRoles` class. Here's an example of how you can use these roles in your code:

```
class WaiiRoles:
    WAII_TRIAL_USER = 'waii-trial-user'
    WAII_USER = 'waii-user'
    WAII_API_USER = 'waii-api-user'
    WAII_ADMIN_USER = 'waii-admin-user'
    WAII_ORG_ADMIN_USER = 'waii-org-admin-user'
    WAII_SUPER_ADMIN_USER = 'waii-super-admin-user'
```

When you create a user in Waii, you can assign one of these roles to them. For example:

```python
# other imports ...
from waii_sdk_py.user import User, CreateUserRequest, WaiiRoles
    
user = User(id=<id>, name=<name>, tenant_id=..., org_id=..., roles=[WaiiRoles.WAII_USER])
WAII.User.create_user(CreateUserRequest(user=user))
```