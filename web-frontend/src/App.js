import React, { useState, useEffect } from "react";
import Dashboard from "./Dashboard";
import Login from "./Login";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user is already logged in
    const authUser = localStorage.getItem('auth_user');
    if (authUser) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('auth_user');
    setIsAuthenticated(false);
  };

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return <Dashboard onLogout={handleLogout} />;
}

export default App;