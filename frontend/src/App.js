import React, { useState, useEffect } from "react";
import "./App.css";
import { signup, login, analyzeMeeting, getHistory } from "./api";
import AuthForm from "./components/AuthForm";
import UploadCard from "./components/UploadCard";
import Dashboard from "./Dashboard";

function App() {
  const [userId, setUserId] = useState(localStorage.getItem("userId") || "");
  const [authMode, setAuthMode] = useState("login");
  const [view, setView] = useState(userId ? "upload" : "auth");
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (userId) {
      getHistory(userId).then(setHistory).catch(console.error);
    }
  }, [userId]);

  async function handleAuthSubmit(username, password) {
    try {
      setLoading(true);
      const data =
        authMode === "login"
          ? await login(username, password)
          : await signup(username, password);
      setUserId(data.user_id);
      localStorage.setItem("userId", data.user_id);
      setView("upload");
    } catch (err) {
      alert(err.response?.data?.detail || "Auth failed");
    } finally {
      setLoading(false);
    }
  }
  
  async function handleAnalyze(file) {
    try {
      setLoading(true);
      const data = await analyzeMeeting(userId, file);
      setAnalysis(data);
      const hist = await getHistory(userId);
      setHistory(hist);
      setView("results");
    } catch (err) {
      console.error(err);
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        err.message ||
        "Analysis failed";
      alert(msg);
    } finally {
      setLoading(false);
    }
  }
  

  function handleLogout() {
    localStorage.removeItem("userId");
    setUserId("");
    setAnalysis(null);
    setHistory([]);
    setView("auth");
  }

  return (
    <div className="app-root">
      <header className="topbar">
        <div className="logo">🗣️ Meeting Clarity Agent</div>
        {userId && (
          <button className="ghost" onClick={handleLogout}>
            Logout
          </button>
        )}
      </header>

      <main className="content">
        {view === "auth" && (
          <AuthForm
            mode={authMode}
            loading={loading}
            onSubmit={handleAuthSubmit}
            onSwitchMode={() =>
              setAuthMode((m) => (m === "login" ? "signup" : "login"))
            }
          />
        )}

        {view === "upload" && (
          <UploadCard loading={loading} onAnalyze={handleAnalyze} />
        )}

        {view === "results" && analysis && (
          <Dashboard
            analysis={analysis}
            history={history}
            onAnalyzeAgain={() => setView("upload")}
          />
        )}
      </main>
    </div>
  );
}

export default App;
