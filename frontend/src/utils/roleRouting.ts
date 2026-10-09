export const employeeRoles = new Set([
  'Employee',
  'Manager',
  'HR',
  'Payroll Administrator',
  'Security Analyst',
]);

export const workspaceRoles = new Set([
  'Manager',
  'HR',
  'Payroll Administrator',
  'Security Analyst',
]);

export function getPostLoginRoute(roleName?: string): string {
  if (roleName === 'SentinelAI Administrator') return '/dashboard';
  if (roleName === 'Employee') return '/employee';
  if (workspaceRoles.has(roleName ?? '')) return '/choose-workspace';
  return '/403';
}