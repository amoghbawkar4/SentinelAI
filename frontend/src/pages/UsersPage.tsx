import { motion } from 'framer-motion';

const roles = [
  {
    id: 1,
    name: 'Manager',
    email: 'manager@company.com',
    role: 'Manager',
  },
  {
    id: 2,
    name: 'HR',
    email: 'hr@company.com',
    role: 'HR',
  },
  {
    id: 3,
    name: 'Employee',
    email: 'employee@company.com',
    role: 'Employee',
  },
  {
    id: 4,
    name: 'Payroll Administrator',
    email: 'payroll@company.com',
    role: 'Payroll Administrator',
  },
  {
    id: 5,
    name: 'Security Analyst',
    email: 'security@company.com',
    role: 'Security Analyst',
  },
];

export default function UsersPage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6"
    >
      <div>
        <h2 className="text-xl font-semibold">User Management</h2>
      </div>

      <div className="mt-6 space-y-3">
        {roles.map((user) => (
          <div
            key={user.id}
            className="flex items-center justify-between gap-4 rounded-2xl border border-slate-800 bg-slate-950/70 p-4"
          >
            {/* User information */}
            <div className="min-w-0">
              <p className="font-medium text-white">
                {user.name}
              </p>

              <p className="mt-1 text-sm text-slate-400">
                {user.email}
              </p>
            </div>

            {/* Role badge */}
            <div className="shrink-0 rounded-full bg-slate-800 px-4 py-2 text-sm text-slate-300">
              {user.role}
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}