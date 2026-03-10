#!/usr/bin/env node
/**
 * Add AINL monitor cron job to OpenClaw.
 * Usage: node add_ainl_cron.js [intervalMinutes=15]
 */
const { CronStore } = require('@openclaw/server');
const path = require('path');
const fs = require('fs');

(async () => {
  const interval = parseInt(process.argv[2] || '15', 10);
  const cronExpression = `*/${interval} * * * *`;
  const command = `/Users/clawdbot/.openclaw/workspace/scripts/run_ainl_monitor.sh`;
  const name = 'AINL Proactive Monitor';
  const description = 'Runs the AINL-based heartbeat and monitoring system every ' + interval + ' minutes.';

  // Find OpenClaw home (usually ~/.openclaw)
  const home = process.env.HOME || process.env.USERPROFILE;
  const openclawHome = path.join(home, '.openclaw');
  const cronDir = path.join(openclawHome, 'cron');

  if (!fs.existsSync(cronDir)) {
    fs.mkdirSync(cronDir, { recursive: true });
  }

  // Build cron job JSON
  const job = {
    name,
    description,
    schedule: { kind: 'cron', cron: cronExpression },
    payload: {
      kind: 'shell',
      command,
      timeoutSeconds: 300
    },
    sessionTarget: 'isolated',
    wakeMode: 'now',
    enabled: true
  };

  // Use CronStore to add
  const store = new CronStore({ dataDir: cronDir });
  await store.add(job);
  console.log(`Added cron job: ${name} (${cronExpression})`);
})().catch(err => {
  console.error('Error adding cron:', err);
  process.exit(1);
});
