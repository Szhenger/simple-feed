/**
 * Structural boundaries for multi-tenant isolation and Shard Routing
 */

export type UserRole = 'ROOT' | 'ADMIN' | 'MEMBER';

export interface Workspace {
  id: string;               // UUID v4 - injected into Row-Level Security checks
  name: string;
  ownerId: string;
  shardKey: string;         // Deterministic key passed to build_databases/ShardRouter
  createdAt: string;
  updatedAt: string;
}

export interface UserContext {
  id: string;
  username: string;
  activeWorkspaceId: string;
  role: UserRole;
  permissions: string[];
}
