// MT5 Expert Advisor stub — generated from .lang
#property strict

input int   Multiplier = 1;
input double LotSize = 0.1;

int OnInit()
{
  return(INIT_SUCCEEDED);
}

void OnTick()
{
  if (!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)) return;
  // TODO: signals from parsed services / symbols
  // MqlTick tick; SymbolInfoTick(_Symbol, tick);
}

void OnDeinit(const int reason) {}
