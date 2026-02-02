import React, { useState } from 'react';
import axios from 'axios';
import './Login.css';

const API_BASE = 'http://127.0.0.1:8000/api';

function Login({ onLoginSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const endpoint = isLogin ? 'auth/login/' : 'auth/register/';
      const data = isLogin
        ? { username, password }
        : { username, password, email };

      const response = await axios.post(`${API_BASE}/${endpoint}`, data);
      
      // Store credentials in localStorage
      localStorage.setItem('auth_user', JSON.stringify({
        username: response.data.username,
        credentials: btoa(`${username}:${password}`),
      }));

      setUsername('');
      setPassword('');
      setEmail('');
      onLoginSuccess();
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1 className="login-title">Chemical Equipment Visualizer</h1>
          <p className="login-subtitle">Analyze and visualize your equipment data</p>
        </div>

        <div className="login-form-wrapper">
          <div className="login-tabs">
            <button
              className={`tab ${isLogin ? 'active' : ''}`}
              onClick={() => setIsLogin(true)}
            >
              Sign In
            </button>
            <button
              className={`tab ${!isLogin ? 'active' : ''}`}
              onClick={() => setIsLogin(false)}
            >
              Sign Up
            </button>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            {error && <div className="error-message">{error}</div>}

            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>

            {!isLogin && (
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  id="email"
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            )}

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button
              type="submit"
              className="submit-button"
              disabled={loading}
            >
              {loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Sign Up')}
            </button>
          </form>
        </div>

        <div className="login-footer">
          <p>Chemical Equipment Analysis Platform</p>
        </div>
      </div>
    </div>
  );
}

export default Login;
