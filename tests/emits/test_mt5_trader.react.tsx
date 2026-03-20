// AINL emitted React/TSX
import React, { useState } from 'react';

export const Trader: React.FC = () => {
  const [positions, setPositions] = useState<Position[]>([]);
  const [signals, setSignals] = useState<Signal[]>([]);
  return (
    <div className="dashboard">
      <h1>Trader</h1>
    </div>
  );
};

export const PositionsTable: React.FC = () => {
  const [data, setData] = useState<any>(null);
  return (
    <div className="dashboard">
      <h1>PositionsTable</h1>
      <DataTable data={positions} />
    </div>
  );
};

export const SignalPanel: React.FC = () => {
  const [data, setData] = useState<any>(null);
  return (
    <div className="dashboard">
      <h1>SignalPanel</h1>
      <DataTable data={signals} />
    </div>
  );
};
