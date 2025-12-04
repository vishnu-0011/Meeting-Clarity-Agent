// src/components/HistoryChart.js
import React from "react";
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

function HistoryChart({ history }) {
  const data = Array.isArray(history)
    ? history.map((h) => ({
        label: new Date(h.created_at).toLocaleString(),
        clarity_index: h.clarity_index,
      }))
    : [];

  if (data.length < 2) {
    return <p>Run at least two meetings to see the trend.</p>;
  }

  return (
    <div style={{ width: "100%", overflowX: "auto" }}>
      <LineChart
        width={600}
        height={260}
        data={data}
        margin={{ top: 10, right: 20, left: 0, bottom: 0 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="label" hide />
        <YAxis />
        <Tooltip />
        <Line
          type="monotone"
          dataKey="clarity_index"
          stroke="#00d9ff"
          strokeWidth={2}
          dot={{ r: 3 }}
        />
      </LineChart>
    </div>
  );
}

export default HistoryChart;
