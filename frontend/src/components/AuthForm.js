import React, { useState } from "react";

function AuthForm({ mode, loading, onSubmit, onSwitchMode }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    onSubmit(username, password);
  }

  return (
    <div className="card auth-card">
      <h2>{mode === "login" ? "Log in" : "Sign up"}</h2>
      <form onSubmit={handleSubmit}>
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          autoComplete="username"
          required
        />
        <input
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          type="password"
          placeholder="Password"
          autoComplete="current-password"
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? "Please wait..." : "Continue"}
        </button>
      </form>
      <p className="switch">
        {mode === "login" ? (
          <>
            Need an account?{" "}
            <button type="button" className="link-btn" onClick={onSwitchMode}>
              Sign up
            </button>
          </>
        ) : (
          <>
            Already have an account?{" "}
            <button type="button" className="link-btn" onClick={onSwitchMode}>
              Log in
            </button>
          </>
        )}
      </p>
    </div>
  );
}

export default AuthForm;
