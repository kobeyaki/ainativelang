#!/usr/bin/env node
// Usage: node post.js "your tweet text"
const { TwitterApi } = require('/tmp/node_modules/twitter-api-v2');

const client = new TwitterApi({
  appKey: process.env.X_API_KEY,
  appSecret: process.env.X_API_SECRET,
  accessToken: process.env.X_ACCESS_TOKEN,
  accessSecret: process.env.X_ACCESS_TOKEN_SECRET,
});

const text = process.argv.slice(2).join(' ');
if (!text) { console.error('Usage: node post.js "tweet text"'); process.exit(1); }

client.v2.tweet(text)
  .then(r => console.log('Posted:', JSON.stringify(r.data)))
  .catch(e => console.error('Error:', e.message, JSON.stringify(e.data)));
