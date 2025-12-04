import React from "react";

function ClarityHero({ clarityIndex, summary, onAnalyzeAgain }) {
  return (
    <div className="hero">
      <h2>Meeting Clarity Index</h2>
      <div className="score">{clarityIndex}/100</div>
      <p className="summary">{summary}</p>
      <button className="primary" onClick={onAnalyzeAgain}>
        Analyze another meeting
      </button>
    </div>
  );
}

export default ClarityHero;
