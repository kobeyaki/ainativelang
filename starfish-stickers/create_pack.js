#!/usr/bin/env node
/**
 * Telegram Sticker Pack Creator
 * Uses Bot API to create a sticker set programmatically
 * 
 * Usage: node create_pack.js <bot_token> <user_id> [pack_name] [pack_title]
 */

const fs = require("fs");
const path = require("path");
const https = require("https");
const FormData = require("form-data");

// Grammy / node-telegram-bot-api for sticker management
const { Bot, InputFile } = require("grammy");

const STICKERS_DIR = path.join(__dirname, "stickers");

const STICKER_EMOJIS = {
  higher:        "🚀",
  ath:           "📈",
  big_buy:       "💰",
  wagmi:         "🙌",
  ngmi:          "😭",
  lfg:           "🔥",
  gm:            "☕",
  diamond_hands: "💎",
  wen_moon:      "🌙",
  rekt:          "📉",
};

async function createStickerPack(botToken, userId, packName, packTitle) {
  const bot = new Bot(botToken);

  const stickers = fs
    .readdirSync(STICKERS_DIR)
    .filter(f => f.endsWith(".png"))
    .sort()
    .map(f => {
      const name = path.basename(f, ".png");
      return {
        file: path.join(STICKERS_DIR, f),
        emoji: STICKER_EMOJIS[name] || "⭐",
        name,
      };
    });

  if (stickers.length === 0) {
    console.error("No PNG stickers found in", STICKERS_DIR);
    process.exit(1);
  }

  console.log(`Creating pack: "${packTitle}" (@${packName})`);
  console.log(`Stickers: ${stickers.length}`);
  console.log(`Owner user ID: ${userId}\n`);

  // Build sticker objects for API
  const stickerObjects = stickers.map(s => ({
    sticker: new InputFile(s.file),
    format: "static",
    emoji_list: [s.emoji],
  }));

  try {
    // Create the sticker set
    await bot.api.createNewStickerSet(
      userId,
      packName,
      packTitle,
      stickerObjects
    );
    console.log(`✅ Pack created! https://t.me/addstickers/${packName}`);
  } catch (err) {
    if (err.message?.includes("STICKERSET_INVALID") || err.message?.includes("already")) {
      console.log("Pack name taken or already exists, trying to add stickers to existing...");
      // Try adding stickers instead
      for (const s of stickers) {
        try {
          await bot.api.addStickerToSet(userId, packName, {
            sticker: new InputFile(s.file),
            format: "static",
            emoji_list: [s.emoji],
          });
          console.log(`  + Added ${s.name} ${s.emoji}`);
        } catch (e) {
          console.log(`  ✗ ${s.name}: ${e.message}`);
        }
      }
    } else {
      throw err;
    }
  }
}

// Main
const [,, botToken, userId, packName, packTitle] = process.argv;

if (!botToken || !userId) {
  console.log("Usage: node create_pack.js <BOT_TOKEN> <USER_ID> [pack_name] [pack_title]");
  console.log("Example: node create_pack.js 123:abc 987654321 starfish_degen_by_mybot 'Starfish Degen'");
  process.exit(0);
}

createStickerPack(
  botToken,
  parseInt(userId),
  packName || "starfish_degen_v1",
  packTitle || "Starfish Degen 🌟"
).catch(console.error);
