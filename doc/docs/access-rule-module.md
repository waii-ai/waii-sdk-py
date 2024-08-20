---
id: access-rule-module
title: Table Access Rules
---


The `Access Rule` module contains methods related to creating access rules to ensure secure access to data for all users

Currently, we support access rules scoped to Tables

### TableAccessRule

A TableAccessRule object has the following fields
- `id`: An optional id for the rule, Waii will fill this in if left blank. This must be unique for every rule
- `name`: A name for help identifying the rule
- `table`: A fully qualified `TableName` object for the table that the rule is scoped to
- `org_id`: The organization id that the rule applies to
- `tenant_id`: The tenant id that the rule applies to, can be `*` if it applies to every tenant in the organization
- `user_id`: The user id that the rule applies to, can be `*` if it applies to every user in the tenant
- `type`: One of `TableAccessRuleType`
  - `block`: Block all access to this table for the corresponding users
  - `filter`: Anytime this table is referenced in a query, protect access to this table with the expression used as the `WHERE` clause to filter the query
- `expression`: An optional expression used as the `WHERE` clause for a filter table access rule. Can contain variables using `{variable_name}`

Variables used in access rules will be resolved using variables in a user's `User`, `Tenant`, and `Organization`
We also have 5 built-in variables that can be used in any access rule (user defined variables take precedence):
- `org_id`: The id of the `Organization` that the current user is a part of
- `tenant_id`: The id of the `Tenant` that the current user is a part of
- `user_id`: The current `User` id
- `roles`: An array of the roles for which the current user owns
- `permissions`: An array of permissions which the current user contains

### Examples
Expression: 
```python
table = TableName(table_name="T", schema_name="S", database_name="D")
expression = col_a > 10
```
Any query that queries table T will refer to the results of the following CTE instead of T
```python
with _access_controlled_t as (
  SELECT *
  FROM t 
  WHERE col_a > 10
)
```

```python
table = TableName(table_name="T", schema_name="S", database_name="D")
expression = ( col_b = {user_id} AND col_c IN ({permissions}) )
```
Any query that queries table T will refer to the results of the following CTE instead of T
```python
with _access_controlled_t as (
  SELECT *
  FROM t 
  WHERE col_b = '<current user id>' AND col_c IN ('array of current user permissions')
)
```

```python
table = TableName(table_name="T", schema_name="S", database_name="D")
expression = col_d IN (SELECT col_d FROM d.s.t2 WHERE t2.col_e = t1.col_e)
```
Any query that queries table T will refer to the results of the following CTE instead of T
```python
with _access_controlled_t as (
  SELECT *
  FROM t 
  WHERE col_d IN (SELECT col_d FROM d.s.t2 WHERE t2.col_e = t1.col_e)
)
```

### Rule Management
- There can only be one rule per (org_id, tenant_id, user_id) per table
- Each rule must have a unique id
- Multiple rules can be scoped to a table, the rule with the tightest scope for a user will be the one that is enforced within the query

## Methods

### UpdateTableAccessRules

```python
WAII.access_rule.update_table_access_rules(params: UpdateTableAccessRuleRequest)
```

This method creates or updates the access rule for a table based on the parameters

Request fields:
- `rules`: A list of table access rules to update

Each rule will be validated and rewritten before any of the rules are saved. An error will be thrown if
- the `table` is invalid
- the `expression` or the derived CTE are invalid (variables will be filled in for any applicable user)
- an existing rule has the same combination of (org_id, tenant_id, user_id) and table, but a different id

A rule will overwrite an existing rule if it has the same (org_id, tenant_id, user_id), table, and id. 
Otherwise, a rule with the same id as an existing rule will be rejected

### DeleteTableAccessRules
```python
WAII.access_rule.remove_table_access_rules(params: RemoveTableAccessRuleRequest)
```
Request fields:
- `rules`: A list of rule ids to remove

### ListTableAccessRules
```python
WAII.access_rule.list_table_access_rules(params: ListTableAccessRuleRequest) -> ListTableAccessRuleResponse
```

This method will list the active table access rules that match the fields in the request.
Request Fields
- `table`: Optional argument, a fully qualified table name. All rules scoped to this table will be listed in the response
- `ids`: Optional argument, a list of access rule ids. All rules matching these ids will be returned in the response
If these arguments are left empty, all active access rules within the scope will be returned

Response fields
- `rules`: The list of rules that match the argments

