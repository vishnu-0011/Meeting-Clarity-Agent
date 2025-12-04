import React from "react";

function SpeakerChart({ speakerScores }) {
  if (!speakerScores || !speakerScores.length) {
    return <p>No speaker scores available.</p>;
  }

  return (
    <ul>
      {speakerScores.map((s) => (
        <li key={s.speaker}>
          {s.speaker}: {s.score.toFixed(2)}
        </li>
      ))}
    </ul>
  );
}

export default SpeakerChart;
