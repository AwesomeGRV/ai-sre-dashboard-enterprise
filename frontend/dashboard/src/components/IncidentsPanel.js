import React, { useState } from 'react';
import axios from 'axios';
import { AlertTriangle, Clock, CheckCircle, XCircle, Brain, ExternalLink } from 'lucide-react';

const IncidentsPanel = ({ incidents }) => {
  const [analyzingIncident, setAnalyzingIncident] = useState(null);

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high':
        return 'bg-red-400/20 text-red-400 border-red-400/30';
      case 'medium':
        return 'bg-yellow-400/20 text-yellow-400 border-yellow-400/30';
      case 'low':
        return 'bg-blue-400/20 text-blue-400 border-blue-400/30';
      default:
        return 'bg-slate-400/20 text-slate-400 border-slate-400/30';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'open':
        return <XCircle className="h-4 w-4 text-red-400" />;
      case 'resolved':
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      default:
        return <Clock className="h-4 w-4 text-yellow-400" />;
    }
  };

  const analyzeIncident = async (incidentId) => {
    setAnalyzingIncident(incidentId);
    try {
      await axios.post(`/incidents/${incidentId}/analyze`);
      // The parent component should refresh data
      window.location.reload();
    } catch (error) {
      console.error('Error analyzing incident:', error);
    } finally {
      setAnalyzingIncident(null);
    }
  };

  if (!incidents || incidents.length === 0) {
    return (
      <div className="dashboard-card">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <AlertTriangle className="h-5 w-5 mr-2 text-yellow-400" />
          Incidents & AI Analysis
        </h3>
        <div className="text-slate-400 text-center py-8">
          No incidents reported. System is running smoothly!
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-card">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
        <AlertTriangle className="h-5 w-5 mr-2 text-yellow-400" />
        Incidents & AI Analysis
      </h3>

      <div className="space-y-4">
        {incidents.map((incident) => (
          <div 
            key={incident.id} 
            className="bg-slate-700/50 rounded-lg p-4 border border-slate-600"
          >
            {/* Incident Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  {getStatusIcon(incident.status)}
                  <h4 className="text-white font-medium">{incident.title}</h4>
                  <span className={`px-2 py-1 rounded text-xs font-medium border ${getSeverityColor(incident.severity)}`}>
                    {incident.severity.toUpperCase()}
                  </span>
                </div>
                <p className="text-slate-400 text-sm">{incident.description}</p>
              </div>
            </div>

            {/* Incident Metadata */}
            <div className="flex items-center gap-4 text-xs text-slate-500 mb-3">
              <span>ID: {incident.id}</span>
              <span>Created: {new Date(incident.created_at).toLocaleString()}</span>
              {incident.resolved_at && (
                <span>Resolved: {new Date(incident.resolved_at).toLocaleString()}</span>
              )}
            </div>

            {/* AI Analysis Section */}
            <div className="border-t border-slate-600 pt-3">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center text-sm">
                  <Brain className="h-4 w-4 mr-2 text-blue-400" />
                  <span className="text-slate-300">AI Analysis</span>
                </div>
                {!incident.ai_analysis && (
                  <button
                    onClick={() => analyzeIncident(incident.id)}
                    disabled={analyzingIncident === incident.id}
                    className="px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white text-xs rounded font-medium flex items-center"
                  >
                    {analyzingIncident === incident.id ? (
                      <>
                        <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-2"></div>
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Brain className="h-3 w-3 mr-1" />
                        Generate Analysis
                      </>
                    )}
                  </button>
                )}
              </div>

              {incident.ai_analysis ? (
                <div className="bg-slate-800/50 rounded p-3 text-sm text-slate-300">
                  <div className="flex items-start gap-2">
                    <Brain className="h-4 w-4 text-blue-400 mt-0.5 flex-shrink-0" />
                    <p>{incident.ai_analysis}</p>
                  </div>
                </div>
              ) : (
                <div className="text-slate-500 text-sm italic">
                  No AI analysis available. Click "Generate Analysis" to get AI-powered insights.
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="mt-6 pt-4 border-t border-slate-700">
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-400">
            Total Incidents: {incidents.length}
          </span>
          <span className="text-slate-400">
            Open: {incidents.filter(i => i.status === 'open').length} | 
            Resolved: {incidents.filter(i => i.status === 'resolved').length}
          </span>
        </div>
      </div>
    </div>
  );
};

export default IncidentsPanel;
