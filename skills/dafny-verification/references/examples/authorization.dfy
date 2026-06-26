datatype Role = Guest | User | Admin
datatype Visibility = Public | Private
datatype UserId = UserId(value: int)
datatype TenantId = TenantId(value: int)

function CanRead(
  role: Role,
  actor: UserId,
  owner: UserId,
  actorTenant: TenantId,
  resourceTenant: TenantId,
  visibility: Visibility
): bool {
  role == Admin ||
  (actorTenant == resourceTenant &&
    (visibility == Public || actor == owner))
}

lemma AdminCanRead(
  actor: UserId,
  owner: UserId,
  actorTenant: TenantId,
  resourceTenant: TenantId,
  visibility: Visibility
)
  ensures CanRead(Admin, actor, owner, actorTenant, resourceTenant, visibility)
{
}

lemma SameTenantPublicCanRead(
  role: Role,
  actor: UserId,
  owner: UserId,
  tenant: TenantId
)
  ensures CanRead(role, actor, owner, tenant, tenant, Public)
{
}

lemma SameTenantOwnerCanRead(role: Role, actor: UserId, tenant: TenantId)
  ensures CanRead(role, actor, actor, tenant, tenant, Private)
{
}

lemma PrivateNonOwnerNonAdminDenied(
  role: Role,
  actor: UserId,
  owner: UserId,
  tenant: TenantId
)
  requires role != Admin
  requires actor != owner
  ensures !CanRead(role, actor, owner, tenant, tenant, Private)
{
}

lemma CrossTenantNonAdminDenied(
  role: Role,
  actor: UserId,
  owner: UserId,
  actorTenant: TenantId,
  resourceTenant: TenantId,
  visibility: Visibility
)
  requires role != Admin
  requires actorTenant != resourceTenant
  ensures !CanRead(role, actor, owner, actorTenant, resourceTenant, visibility)
{
}
