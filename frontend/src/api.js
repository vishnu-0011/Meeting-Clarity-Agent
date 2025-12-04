import axios from "axios";

const API_BASE = "http://localhost:8000/api";

export async function signup(username, password) {
  const res = await axios.post(`${API_BASE}/signup`, { username, password });
  return res.data; // { user_id }
}

export async function login(username, password) {
  const res = await axios.post(`${API_BASE}/login`, { username, password });
  return res.data;
}

export async function analyzeMeeting(userId, file) {
  const formData = new FormData();
  formData.append("user_id", userId);
  formData.append("file", file);

  const res = await axios.post(`${API_BASE}/analyze`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function getHistory(userId) {
  const res = await axios.get(`${API_BASE}/history/${userId}`);
  return res.data.history;
}

