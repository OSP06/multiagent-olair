import React from "react";

interface ClauseViewerProps {
  clause: string;
  risk: string;
  suggestion?: string;
}

const ClauseViewer: React.FC<ClauseViewerProps> = ({ clause, risk, suggestion }) => {
  return (
    <div style={{ marginBottom: "1rem", padding: "1rem", border: "1px solid #ccc" }}>
      <p><strong>Clause:</strong> {clause}</p>
      <p><strong>Risk:</strong> {risk}</p>
      {suggestion && <p><strong>Redline Suggestion:</strong> {suggestion}</p>}
    </div>
  );
};

export default ClauseViewer;
export {};
