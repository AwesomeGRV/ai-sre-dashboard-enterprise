import React from 'react';
import { CheckCircle, AlertTriangle, XCircle, Server } from 'lucide-react';

const HealthOverview = ({ data }) => {
  if (!data) return null;

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-green-400" />;
      case 'degraded':
        return <AlertTriangle className="h-5 w-5 text-yellow-400" />;
      case 'unhealthy':
        return <XCircle className="h-5 w-5 text-red-400" />;
      default:
        return <Server className="h-5 w-5 text-slate-400" />;
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'healthy':
        return 'status-healthy';
      case 'degraded':
        return 'status-degraded';
      case 'unhealthy':
        return 'status-unhealthy';
      default:
        return 'text-slate-400';
    }
  };

  return (
    <div className="dashboard-card mb-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-white">System Health Overview</h2>
        <div className={`flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusClass(data.status)}`}>
          {getStatusIcon(data.status)}
          <span className="ml-2">{data.status.toUpperCase()}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {Object.entries(data.services).map(([serviceName, service]) => (
          <div key={serviceName} className="bg-slate-700/50 rounded-lg p-4 border border-slate-600">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-slate-300 capitalize">
                {serviceName.replace('_', ' ')}
              </h3>
              {getStatusIcon(service.status)}
            </div>
            <div className="text-xs text-slate-400">
              <div>Status: <span className={`font-medium ${getStatusClass(service.status)}`}>{service.status}</span></div>
              <div>URL: <span className="font-mono text-slate-500">{service.url}</span></div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 text-xs text-slate-400">
        Last updated: {new Date(data.timestamp).toLocaleString()}
      </div>
    </div>
  );
};

export default HealthOverview;
