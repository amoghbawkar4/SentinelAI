import { describe, expect, it } from 'vitest';
import { getPostLoginRoute, workspaceRoles } from './roleRouting';

describe('getPostLoginRoute', () => {
  it.each([
    ['Employee', '/employee'],
    ['HR', '/choose-workspace'],
    ['Manager', '/choose-workspace'],
    ['Payroll Administrator', '/choose-workspace'],
    ['Security Analyst', '/choose-workspace'],
    ['SentinelAI Administrator', '/dashboard'],
  ])('routes %s to %s', (role, route) => {
    expect(getPostLoginRoute(role)).toBe(route);
  });

  it('does not grant a destination to an unknown or missing role', () => {
    expect(getPostLoginRoute('Unknown Role')).toBe('/403');
    expect(getPostLoginRoute()).toBe('/403');
  });

  it('limits workspace access to the intended higher-level roles', () => {
    expect([...workspaceRoles]).toEqual(['Manager', 'HR', 'Payroll Administrator', 'Security Analyst']);
    expect(workspaceRoles.has('Employee')).toBe(false);
    expect(workspaceRoles.has('SentinelAI Administrator')).toBe(false);
  });
});