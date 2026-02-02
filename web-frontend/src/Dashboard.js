import React, { useEffect, useState, useRef } from "react";
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
  const [selectedId, setSelectedId] = useState(null);
  const [summary, setSummary] = useState(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const barChartRef = useRef(null);
  const pieChartRef = useRef(null);

  // Get authentication headers
  const getAuthHeaders = () => {
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
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      const res = await axios.get(`${API_BASE}/datasets/`, getAuthHeaders());
      setDatasets(res.data);
    } catch (error) {
      if (error.response?.status === 401) {
        onLogout();
      }
    }
  };

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
      alert("Error uploading file");
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
    } catch (err) {
      setSummary(null);
    }
  };

  const deleteDataset = async (id) => {
    if (window.confirm("Are you sure you want to delete this dataset?")) {
      try {
        const response = await axios.delete(`${API_BASE}/datasets/${id}/`, getAuthHeaders());
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

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="header-top">
            <div>
              <h1 className="title">Chemical Equipment Visualizer</h1>
              <p className="subtitle">Analyze and visualize your equipment data</p>
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
            <h2 className="section-title">📁 Your Datasets</h2>
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
