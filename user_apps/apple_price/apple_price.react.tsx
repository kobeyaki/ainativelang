// AINL emitted React/TSX
import React, { useState } from 'react';

export const ApplePrice: React.FC = () => {
  const [quote, setQuote] = useState<Json>(null);
  return (
    <div className="dashboard">
      <h1>ApplePrice</h1>
      <DataTable data={quote} />
    </div>
  );
};


