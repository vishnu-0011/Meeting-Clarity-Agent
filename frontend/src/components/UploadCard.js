import React, { useState } from "react";

function UploadCard({ loading, onAnalyze }) {
  const [file, setFile] = useState(null);

  function handleSubmit(e) {
    e.preventDefault();
    if (!file) {
      alert("Please choose an MP4 video");
      return;
    }
    onAnalyze(file);
  }

  return (
    <div className="card upload-card">
      <h2>Upload meeting video</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept="video/mp4"
          onChange={(e) => setFile(e.target.files[0] || null)}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Analyzing..." : "Analyze clarity"}
        </button>
      </form>
    </div>
  );
}

export default UploadCard;
