import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, AlertTriangle, CheckCircle, XCircle, TrendingUp, Clock, Server, Cpu } from 'lucide-react';
import HealthOverview from './components/HealthOverview';
import MetricsChart from './components/MetricsChart';
import IncidentsPanel from './components/IncidentsPanel';
import SLAMetrics from './components/SLAMetrics';

function App() {
  const [healthData, setHealthData] = useState(null);
  const [metrics, setMetrics] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [slaData, setSlaData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [healthRes, metricsRes, incidentsRes, slaRes] = await Promise.all([
        axios.get('/health'),
        axios.get('/metrics'),
        axios.get('/incidents'),
        axios.get('/sla')
      ]);

      setHealthData(healthRes.data);
      setMetrics(metricsRes.data);
      setIncidents(incidentsRes.data);
      setSlaData(slaRes.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to fetch data from backend');
    } finally {
      setLoading(false);
    }
  };

  const generateDemoIncidents = async () => {
    try {
      await axios.post('/demo/generate-incidents');
      fetchData();
    } catch (err) {
      console.error('Error generating demo incidents:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading SRE Dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-red-400 text-xl">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <Activity className="h-8 w-8 text-blue-400 mr-3" />
              <h1 className="text-2xl font-bold text-white">AI-Powered SRE Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={generateDemoIncidents}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Generate Demo Incidents
              </button>
              <span className="text-slate-400 text-sm">
                Last updated: {new Date().toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Health Overview */}
        <HealthOverview data={healthData} />

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <MetricsChart metrics={metrics} />
          <SLAMetrics data={slaData} />
        </div>

        {/* Incidents Panel */}
        <IncidentsPanel incidents={incidents} />
      </main>
    </div>
  );
}

export default App;
