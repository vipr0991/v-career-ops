#!/usr/bin/env node
/**
 * Career-Ops Multi-Service Launcher
 * Starts backend API and frontend dev server in parallel
 */

const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

const isWindows = os.platform() === 'win32';
const rootDir = __dirname;

console.log('\n');
console.log('============================================================');
console.log('               CAREER-OPS LAUNCHER');
console.log('============================================================');
console.log('\n');

let backendReady = false;
let frontendReady = false;

// Start Backend (Python API)
console.log('Starting Backend (Python API on port 5000)...');
const backendProc = spawn('python', ['career_ops_api.py'], {
  cwd: rootDir,
  stdio: 'inherit',
  shell: isWindows
});

backendProc.on('error', (err) => {
  console.error('Backend failed to start:', err.message);
  process.exit(1);
});

// Wait a bit for backend to start
setTimeout(() => {
  // Start Frontend (React Dev Server)
  console.log('\nStarting Frontend (React dev server on port 5173)...\n');
  
  const frontendProc = spawn(
    isWindows ? 'npm.cmd' : 'npm',
    ['run', 'dev'],
    {
      cwd: path.join(rootDir, 'dashboard-web'),
      stdio: 'inherit',
      shell: isWindows
    }
  );

  frontendProc.on('error', (err) => {
    console.error('Frontend failed to start:', err.message);
    process.exit(1);
  });

  // Handle cleanup
  process.on('SIGINT', () => {
    console.log('\n\nShutting down services...');
    backendProc.kill();
    frontendProc.kill();
    process.exit(0);
  });
}, 2000);

// Handle backend shutdown
backendProc.on('exit', (code) => {
  console.log('\nBackend exited with code:', code);
  process.exit(code);
});
