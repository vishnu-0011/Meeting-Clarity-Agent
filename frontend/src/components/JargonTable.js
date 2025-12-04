import React from "react";

function JargonTable({ topTerms }) {
  if (!topTerms || !topTerms.length) {
    return <p>No high‑impact jargon detected.</p>;
  }

  return (
    <table className="jargon-table">
      <thead>
        <tr>
          <th>Term</th>
          <th>Freq</th>
          <th>Weight</th>
        </tr>
      </thead>
      <tbody>
        {topTerms.map((t) => (
          <tr key={t.term}>
            <td>{t.term}</td>
            <td>{t.freq}</td>
            <td>{t.weight}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default JargonTable;
