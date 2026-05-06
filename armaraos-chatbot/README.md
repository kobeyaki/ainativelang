# ArmaraOS × Pump.fun Chat Controller

Chat-controlled ArmaraOS live stream integration for the AINL token.

## Setup (Windows — one time)

1. **Install Node.js** if you don't have it: https://nodejs.org (LTS version)

2. **Copy this folder to your Windows machine** (USB, zip, or git clone)

3. **Open PowerShell inside the folder** and run:
   ```powershell
   npm install
   ```

4. **Make sure ArmaraOS is running** (it should be at http://localhost:4200)

## Running the Bot

```powershell
node bot.js
```

You'll see:
```
╔═══════════════════════════════════════════╗
║   ArmaraOS × Pump.fun Chat Controller    ║
╚═══════════════════════════════════════════╝
[ArmaraOS] ✓ Reachable
[pump.fun] Connecting...
[pump.fun] Connected
[pump.fun] Subscribing to coin: 56hrCR3n7...
```

## OBS Overlay (optional but recommended)

1. In OBS, add a **Browser Source**
2. Check **"Local file"** and point it to `overlay.html` in this folder
3. Set width: **800**, height: **180**
4. Position it at the bottom of your stream

The overlay will show in real-time:
- Who sent the command
- What prompt they sent
- ArmaraOS's reply

## How chat controls ArmaraOS

Viewers type in pump.fun chat:
```
probe bot <any prompt or command>
```

Examples:
```
probe bot what can you do?
probe bot search the web for AI news
probe bot write a haiku about deterministic execution
probe bot run the weather agent
```

## Safety Rules (hardcoded, cannot be bypassed)

The following are **always blocked**, no exceptions:
- Anything involving buy / sell / send / transfer / wallet
- Private keys, seed phrases, API keys, .env files
- Destructive system commands (rm -rf, del /f, format, shutdown)
- Solana / SOL / pump.fun references

Additional limits:
- **15 second cooldown** per user (prevents spam)
- **Max 300 characters** per prompt
- **Max 3 concurrent commands** in flight

## Files

| File | Purpose |
|------|---------|
| `bot.js` | Main bot — connects to pump.fun, routes to ArmaraOS |
| `overlay.html` | OBS browser source overlay |
| `overlay.json` | Written by bot in real-time, read by overlay |
| `package.json` | Node dependencies |
