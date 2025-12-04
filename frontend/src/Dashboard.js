import React from "react";
import ClarityHero from "./components/ClarityHero";
import SpeakerChart from "./components/SpeakerChart";
import JargonTable from "./components/JargonTable";
import HistoryChart from "./components/HistoryCharts"; // if you created this

function Dashboard({ analysis, history, onAnalyzeAgain }) {
  return (
    <div className="card results-card">
      <ClarityHero
        clarityIndex={analysis.clarity_index}
        summary={analysis.overall_summary}
        onAnalyzeAgain={onAnalyzeAgain}
      />

      <div className="metrics-row">
        <div className="metric">
          <span className="label">Total words</span>
          <span className="value">{analysis.total_words}</span>
        </div>
        <div className="metric">
          <span className="label">Jargon terms</span>
          <span className="value">{analysis.total_jargon_count}</span>
        </div>
        <div className="metric">
          <span className="label">Speakers</span>
          <span className="value">{analysis.speaker_scores.length}</span>
        </div>
      </div>

      <h3>Clarity trend</h3>
      {Array.isArray(history) && history.length > 0 ? (
        <HistoryChart history={history} />
      ) : (
        <p>No history yet. Run at least one meeting.</p>
      )}
 

      <h3>Speaker scores</h3>
      <SpeakerChart speakerScores={analysis.speaker_scores} />

      <h3>Top jargon terms</h3>
      <JargonTable topTerms={analysis.top_jargon_terms} />

      <h3>Transcript</h3>
      <div className="transcript-box">{analysis.transcript}</div>
    </div>
  );
}

export default Dashboard;
