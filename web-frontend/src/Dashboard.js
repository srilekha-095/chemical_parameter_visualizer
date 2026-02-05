import React, { useEffect, useState, useRef, useCallback } from "react";
import axios from "axios";
import { Bar, Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  ArcElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";
import "./Dashboard.css";

ChartJS.register(
  BarElement,
  ArcElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
);

const API_BASE = "http://127.0.0.1:8000/api";

function Dashboard({ onLogout }) {
  const [datasets, setDatasets] = useState([]);
  const [users, setUsers] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [summary, setSummary] = useState(null);
  const [records, setRecords] = useState([]);
  const [filtersMeta, setFiltersMeta] = useState({
    available_types: [],
    pressure_range: null,
    temperature_range: null,
    name_supported: false,
    total: 0,
  });
  const [filters, setFilters] = useState({
    type: "",
    name: "",
    pressureMin: "",
    pressureMax: "",
    temperatureMin: "",
    temperatureMax: "",
  });
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const barChartRef = useRef(null);
  const pieChartRef = useRef(null);
  const storedUser = (() => {
    try {
      return JSON.parse(localStorage.getItem('auth_user') || '{}');
    } catch (err) {
      return {};
    }
  })();
  const isAdmin = storedUser.is_admin === true;
  const currentUserId = storedUser.id;

  // Get authentication headers
  const getAuthHeaders = useCallback(() => {
    const authUser = localStorage.getItem('auth_user');
    if (authUser) {
      const { credentials } = JSON.parse(authUser);
      return {
        headers: {
          'Authorization': `Basic ${credentials}`
        }
      };
    }
    return {};
  }, []);

  const fetchDatasets = useCallback(async () => {
    try {
      const res = await axios.get(`${API_BASE}/datasets/`, getAuthHeaders());
      setDatasets(res.data);
    } catch (error) {
      if (error.response?.status === 401) {
        onLogout();
      }
    }
  }, [getAuthHeaders, onLogout]);

  const fetchUsers = useCallback(async () => {
    try {
      const res = await axios.get(`${API_BASE}/admin/users/`, getAuthHeaders());
      setUsers(res.data);
    } catch (error) {
      if (error.response?.status === 401) {
        onLogout();
      }
    }
  }, [getAuthHeaders, onLogout]);

  useEffect(() => {
    fetchDatasets();
    if (isAdmin) {
      fetchUsers();
    }
  }, [fetchDatasets, fetchUsers, isAdmin]);

  const uploadCSV = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      await axios.post(`${API_BASE}/datasets/`, formData, getAuthHeaders());
      setFile(null);
      // Clear the file input value so the same file can be uploaded again
      const fileInput = document.getElementById("file-input");
      if (fileInput) fileInput.value = "";
      fetchDatasets();
    } catch (err) {
      alert("Error uploading file: " + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = async (datasetId) => {
    try {
      const response = await axios.get(
        `${API_BASE}/datasets/${datasetId}/download_pdf/`,
        { 
          ...getAuthHeaders(),
          responseType: 'blob'
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `dataset_${datasetId}_report.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentElement.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert("Error downloading PDF");
    }
  };

  const loadSummary = async (id) => {
    setSelectedId(id);
    try {
      const res = await axios.get(`${API_BASE}/datasets/${id}/summary/`, getAuthHeaders());
      setSummary(res.data);
      const resetFilters = {
        type: "",
        name: "",
        pressureMin: "",
        pressureMax: "",
        temperatureMin: "",
        temperatureMax: "",
      };
      setFilters(resetFilters);
      await fetchRecords(id, resetFilters);
    } catch (err) {
      alert("Error loading summary: " + (err.response?.data?.error || err.message));
      setSummary(null);
      setRecords([]);
    }
  };

  const deleteDataset = async (id) => {
    if (window.confirm("Are you sure you want to delete this dataset?")) {
      try {
        await axios.delete(`${API_BASE}/datasets/${id}/`, getAuthHeaders());
        // Clear the summary if the deleted dataset was being viewed
        if (selectedId === id) {
          setSummary(null);
          setSelectedId(null);
        }
        // Refresh the datasets list
        await fetchDatasets();
      } catch (err) {
        console.error("Error deleting dataset:", err);
        alert("Error deleting dataset: " + (err.response?.data?.error || err.message));
      }
    }
  };

  const deleteUser = async (id) => {
    if (window.confirm("Are you sure you want to delete this user?")) {
      try {
        await axios.delete(`${API_BASE}/admin/users/${id}/`, getAuthHeaders());
        await fetchUsers();
        await fetchDatasets();
      } catch (err) {
        alert("Error deleting user: " + (err.response?.data?.error || err.message));
      }
    }
  };

  const downloadChart = () => {
    // Get canvas images from both charts
    const barImage = barChartRef.current.toBase64Image();
    const pieImage = pieChartRef.current.toBase64Image();

    // Create a new canvas to combine both images
    const combinedCanvas = document.createElement('canvas');
    combinedCanvas.width = 1400; // Width for 2 charts side by side
    combinedCanvas.height = 500;
    const ctx = combinedCanvas.getContext('2d');

    // Fill background with white
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, combinedCanvas.width, combinedCanvas.height);

    // Create image objects
    const barImg = new Image();
    const pieImg = new Image();

    let imagesLoaded = 0;

    barImg.onload = () => {
      imagesLoaded++;
      if (imagesLoaded === 2) {
        // Draw both images on the canvas
        ctx.drawImage(barImg, 0, 0, 700, 500);
        ctx.drawImage(pieImg, 700, 0, 700, 500);

        // Download the combined image
        combinedCanvas.toBlob((blob) => {
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = 'equipment_charts.png';
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
        });
      }
    };

    pieImg.onload = () => {
      imagesLoaded++;
      if (imagesLoaded === 2) {
        // Draw both images on the canvas
        ctx.drawImage(barImg, 0, 0, 700, 500);
        ctx.drawImage(pieImg, 700, 0, 700, 500);

        // Download the combined image
        combinedCanvas.toBlob((blob) => {
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = 'equipment_charts.png';
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
        });
      }
    };

    barImg.src = barImage;
    pieImg.src = pieImage;
  };

  const fetchRecords = async (datasetId, filterState) => {
    if (!datasetId) return;
    const params = {};
    if (filterState.type) params.type = filterState.type;
    if (filterState.name) params.name = filterState.name;
    if (filterState.pressureMin !== "") params.pressure_min = filterState.pressureMin;
    if (filterState.pressureMax !== "") params.pressure_max = filterState.pressureMax;
    if (filterState.temperatureMin !== "") params.temperature_min = filterState.temperatureMin;
    if (filterState.temperatureMax !== "") params.temperature_max = filterState.temperatureMax;

    try {
      const res = await axios.get(
        `${API_BASE}/datasets/${datasetId}/records/`,
        { ...getAuthHeaders(), params }
      );
      setRecords(res.data.records || []);
      setFiltersMeta({
        available_types: res.data.available_types || [],
        pressure_range: res.data.pressure_range || null,
        temperature_range: res.data.temperature_range || null,
        name_supported: res.data.name_supported === true,
        total: res.data.total || 0,
      });
    } catch (err) {
      alert("Error loading records: " + (err.response?.data?.error || err.message));
      setRecords([]);
    }
  };

  const applyFilters = async () => {
    await fetchRecords(selectedId, filters);
  };

  const clearFilters = async () => {
    const reset = {
      type: "",
      name: "",
      pressureMin: "",
      pressureMax: "",
      temperatureMin: "",
      temperatureMax: "",
    };
    setFilters(reset);
    await fetchRecords(selectedId, reset);
  };

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="header-top">
            <div>
              <h1 className="title">Chemical Equipment Visualizer</h1>
              <p className="subtitle">Analyze and visualize your equipment data</p>
              {isAdmin && <span className="admin-badge">Admin</span>}
            </div>
            <button onClick={onLogout} className="btn btn-small logout-btn">
              🚪 Logout
            </button>
          </div>
        </div>
      </header>

      <div className="container">
        {/* Main Grid */}
        <div className="main-grid">
          {/* Upload Section */}
          <section className="card upload-section">
            <h2 className="section-title">📊 Upload Dataset</h2>
            <div className="upload-area">
              <input
                type="file"
                id="file-input"
                onChange={(e) => setFile(e.target.files[0])}
                className="file-input"
                accept=".csv"
              />
              <label htmlFor="file-input" className="file-label">
                {file ? file.name : "Choose a CSV file"}
              </label>
              <button
                onClick={uploadCSV}
                disabled={!file || loading}
                className="btn btn-primary"
              >
                {loading ? "Uploading..." : "Upload CSV"}
              </button>
            </div>
          </section>

          {/* Datasets List */}
          <section className="card datasets-section">
            <h2 className="section-title">
              {isAdmin ? "📁 All Datasets" : "📁 Your Datasets"}
            </h2>
            {datasets.length === 0 ? (
              <p className="empty-state">No datasets yet. Upload one to get started.</p>
            ) : (
              <div className="datasets-list">
                {datasets.map((d) => (
                  <div
                    key={d.id}
                    className={`dataset-item ${selectedId === d.id ? "active" : ""}`}
                  >
                    <div className="dataset-info">
                      <p className="dataset-name">Dataset #{d.id}</p>
                      {isAdmin && d.owner && (
                        <span className="dataset-owner">
                          Owner: {d.owner.username} (#{d.owner.id})
                        </span>
                      )}
                      <span className="dataset-date">Uploaded recently</span>
                    </div>
                    <div className="dataset-actions">
                      <button
                        onClick={() => loadSummary(d.id)}
                        className="btn btn-small btn-secondary"
                      >
                        View
                      </button>
                      <button
                        onClick={() => deleteDataset(d.id)}
                        className="btn btn-small btn-danger"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>

        {isAdmin && (
          <section className="card admin-section">
            <h2 className="section-title">User Management</h2>
            {users.length === 0 ? (
              <p className="empty-state">No users found.</p>
            ) : (
              <div className="users-list">
                {users.map((user) => (
                  <div key={user.id} className="user-item">
                    <div className="user-info">
                      <p className="user-name">{user.username}</p>
                      <span className="user-meta">
                        {user.email || "No email"} â€¢ ID #{user.id}
                        {(user.is_staff || user.is_superuser) && " â€¢ Admin"}
                      </span>
                    </div>
                    <div className="user-actions">
                      <button
                        className="btn btn-small btn-danger"
                        onClick={() => deleteUser(user.id)}
                        disabled={user.id === currentUserId}
                        title={user.id === currentUserId ? "You cannot delete yourself" : "Delete user"}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {/* Summary Section */}
        {summary && (
          <section className="card summary-section">
            <div className="summary-header">
              <h2 className="section-title">📈 Analysis Summary</h2>
              <button
                onClick={() => setSummary(null)}
                className="btn-close"
                title="Close summary"
              >
                ✕
              </button>
            </div>

            {/* Stats Grid */}
            <div className="stats-grid">
              <div className="stat-card">
                <p className="stat-label">Total Equipment</p>
                <p className="stat-value">{summary.total_equipment}</p>
              </div>
              <div className="stat-card">
                <p className="stat-label">Avg Flowrate</p>
                <p className="stat-value">{summary.average_flowrate.toFixed(2)}</p>
              </div>
              <div className="stat-card">
                <p className="stat-label">Avg Pressure</p>
                <p className="stat-value">{summary.average_pressure.toFixed(2)}</p>
              </div>
              <div className="stat-card">
                <p className="stat-label">Avg Temperature</p>
                <p className="stat-value">{summary.average_temperature.toFixed(2)}</p>
              </div>
            </div>

            {/* Charts Grid */}
            <div className="charts-grid">
              <div className="chart-container">
                <h3 className="chart-title">Equipment Distribution (Bar)</h3>
                <Bar
                  ref={barChartRef}
                  data={{
                    labels: Object.keys(summary.equipment_type_distribution),
                    datasets: [
                      {
                        label: "Equipment Count",
                        data: Object.values(summary.equipment_type_distribution),
                        backgroundColor: "#3b82f6",
                        borderRadius: 6,
                        borderSkipped: false,
                      },
                    ],
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                      legend: { display: true, position: "top" },
                    },
                  }}
                />
              </div>

              <div className="chart-container">
                <h3 className="chart-title">Equipment Distribution (Pie)</h3>
                <Pie
                  ref={pieChartRef}
                  data={{
                    labels: Object.keys(summary.equipment_type_distribution),
                    datasets: [
                      {
                        data: Object.values(summary.equipment_type_distribution),
                        backgroundColor: [
                          "#3b82f6",
                          "#10b981",
                          "#f59e0b",
                          "#ef4444",
                          "#8b5cf6",
                          "#ec4899",
                        ],
                        borderColor: "#ffffff",
                        borderWidth: 2,
                      },
                    ],
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                      legend: { position: "right" },
                    },
                  }}
                />
              </div>
            </div>

            {/* Export Buttons */}
            <div className="export-buttons">
              <button onClick={downloadChart} className="btn btn-primary">
                🖼️ Export Chart as Image
              </button>
              <button onClick={() => downloadPDF(selectedId)} className="btn btn-primary">
                📄 Download PDF Report
              </button>
            </div>

            {/* Filters */}
            <div className="filters-panel">
              <div className="filters-header">
                <h3 className="filters-title">Filter Equipment</h3>
                <span className="filters-count">
                  {filtersMeta.total} result{filtersMeta.total === 1 ? "" : "s"}
                </span>
              </div>
              <div className="filters-grid">
                <div className="filter-group">
                  <label>Equipment Type</label>
                  <select
                    value={filters.type}
                    onChange={(e) => setFilters({ ...filters, type: e.target.value })}
                  >
                    <option value="">All types</option>
                    {filtersMeta.available_types.map((type) => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>

                <div className="filter-group">
                  <label>Search Name</label>
                  <input
                    type="text"
                    placeholder={filtersMeta.name_supported ? "Search equipment name" : "Name column not available"}
                    value={filters.name}
                    disabled={!filtersMeta.name_supported}
                    onChange={(e) => setFilters({ ...filters, name: e.target.value })}
                  />
                </div>

                <div className="filter-group">
                  <label>Pressure Min</label>
                  <input
                    type="number"
                    step="any"
                    placeholder={filtersMeta.pressure_range ? `${filtersMeta.pressure_range.min}` : "Min"}
                    value={filters.pressureMin}
                    onChange={(e) => setFilters({ ...filters, pressureMin: e.target.value })}
                  />
                </div>

                <div className="filter-group">
                  <label>Pressure Max</label>
                  <input
                    type="number"
                    step="any"
                    placeholder={filtersMeta.pressure_range ? `${filtersMeta.pressure_range.max}` : "Max"}
                    value={filters.pressureMax}
                    onChange={(e) => setFilters({ ...filters, pressureMax: e.target.value })}
                  />
                </div>

                <div className="filter-group">
                  <label>Temperature Min</label>
                  <input
                    type="number"
                    step="any"
                    placeholder={filtersMeta.temperature_range ? `${filtersMeta.temperature_range.min}` : "Min"}
                    value={filters.temperatureMin}
                    onChange={(e) => setFilters({ ...filters, temperatureMin: e.target.value })}
                  />
                </div>

                <div className="filter-group">
                  <label>Temperature Max</label>
                  <input
                    type="number"
                    step="any"
                    placeholder={filtersMeta.temperature_range ? `${filtersMeta.temperature_range.max}` : "Max"}
                    value={filters.temperatureMax}
                    onChange={(e) => setFilters({ ...filters, temperatureMax: e.target.value })}
                  />
                </div>
              </div>
              <div className="filters-actions">
                <button className="btn btn-secondary" onClick={clearFilters}>
                  Clear
                </button>
                <button className="btn btn-primary" onClick={applyFilters}>
                  Apply Filters
                </button>
              </div>
            </div>

            {/* Records Table */}
            <div className="records-table-wrapper">
              {records.length === 0 ? (
                <p className="records-empty">No records match the selected filters.</p>
              ) : (
                <table className="records-table">
                  <thead>
                    <tr>
                      {filtersMeta.name_supported && <th>Equipment Name</th>}
                      <th>Type</th>
                      <th>Flowrate</th>
                      <th>Pressure</th>
                      <th>Temperature</th>
                    </tr>
                  </thead>
                  <tbody>
                    {records.map((rec, idx) => (
                      <tr key={`${rec.type}-${idx}`}>
                        {filtersMeta.name_supported && <td>{rec.name || "-"}</td>}
                        <td>{rec.type}</td>
                        <td>{rec.flowrate}</td>
                        <td>{rec.pressure}</td>
                        <td>{rec.temperature}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </section>
        )}

        {/* Empty State */}
        {!summary && selectedId && (
          <section className="card empty-summary">
            <p>No data available for this dataset.</p>
          </section>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
