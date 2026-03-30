// Token balance verification for $AINL holders on Solana (Token2022)
require('dotenv').config({ path: __dirname + '/.env' });
const { Connection, PublicKey } = require('@solana/web3.js');

const AINL_MINT = new PublicKey(process.env.AINL_TOKEN_MINT);
const TOKEN_2022_PROGRAM = new PublicKey('TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb');
const DECIMALS = 6;
const connection = new Connection(process.env.SOLANA_RPC, 'confirmed');

// Tiers in human-readable amounts (will multiply by 10^decimals)
const TIER_MULTIPLIER = BigInt(10 ** DECIMALS);
const TIERS = {
  whale: BigInt(process.env.TIER_WHALE) * TIER_MULTIPLIER,
  pro: BigInt(process.env.TIER_PRO) * TIER_MULTIPLIER,
  basic: BigInt(process.env.TIER_BASIC) * TIER_MULTIPLIER,
};

async function getAINLBalance(walletAddress) {
  try {
    const wallet = new PublicKey(walletAddress);

    // Get all Token2022 accounts for this wallet
    const accounts = await connection.getParsedTokenAccountsByOwner(wallet, {
      programId: TOKEN_2022_PROGRAM,
    });

    // Find the AINL token account
    for (const { account } of accounts.value) {
      const parsed = account.data.parsed;
      if (parsed.info.mint === AINL_MINT.toBase58()) {
        return BigInt(parsed.info.tokenAmount.amount);
      }
    }
    return BigInt(0);
  } catch (e) {
    console.error('Balance check error:', e.message);
    return BigInt(0);
  }
}

function getTier(balance) {
  if (balance >= TIERS.whale) return { tier: 'whale', emoji: '🐋', name: 'Whale' };
  if (balance >= TIERS.pro) return { tier: 'pro', emoji: '⭐', name: 'Pro' };
  if (balance >= TIERS.basic) return { tier: 'basic', emoji: '🤖', name: 'Basic' };
  return { tier: 'none', emoji: '❌', name: 'Not enough $AINL' };
}

function formatBalance(rawBalance) {
  const whole = rawBalance / TIER_MULTIPLIER;
  const remainder = rawBalance % TIER_MULTIPLIER;
  return `${whole.toLocaleString()}${remainder > 0 ? '.' + remainder.toString().padStart(DECIMALS, '0').replace(/0+$/, '') : ''}`;
}

async function verifyHolder(walletAddress) {
  const balance = await getAINLBalance(walletAddress);
  const tierInfo = getTier(balance);
  return {
    wallet: walletAddress,
    balance: balance.toString(),
    balanceFormatted: formatBalance(balance),
    decimals: DECIMALS,
    ...tierInfo,
  };
}

module.exports = { getAINLBalance, getTier, verifyHolder, formatBalance, TIERS, DECIMALS };
