#!/usr/bin/env node
/**
 * Career-Ops Frontend Dev Server Launcher
 * Minimal wrapper around npm run dev
 */

const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

const isWindows = os.platform() === 'win32';

console.log('\n' + '='.repeat(60));
console.log('  CAREER-OPS FRONTEND DEV SERVER');
console.log('='.repeat(60) + '\n');

const dashboardDir = path.join(__dirname, 'dashboard-web');

console.log('[1/2] Checking dependencies...');
try {
  require.resolve('react');
  console.log('  ✓ Dependencies OK\n');
} catch {
  console.log('  ✗ Dependencies missing');
  console.log('  Fix: cd dashboard-web && npm install\n');
  process.exit(1);
}

console.log('[2/2] Starting dev server on http://localhost:5173');
console.log('  This window must stay open!\n');
console.log('  Press CTRL+C to stop\n');
console.log('-'.repeat(60) + '\n');

// Start dev server
const child = spawn(
  isWindows ? 'npm.cmd' : 'npm',
  ['run', 'dev'],
  {
    cwd: dashboardDir,
    stdio: 'inherit',
    shell: isWindows
  }
);

child.on('error', (err) => {
  console.error('\n✗ Failed to start:', err.message);
  process.exit(1);
});

child.on('exit', (code) => {
  console.log('\n\nShutdown');
  process.exit(code);
});

// Handle interrupt
process.on('SIGINT', () => {
  console.log('\n\nShutting down...');
  child.kill();
  process.exit(0);
});
