import React from 'react';
import { Target, Clock, TrendingUp, AlertTriangle } from 'lucide-react';

const SLAMetrics = ({ data }) => {
  if (!data) {
    return (
      <div className="dashboard-card">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <Target className="h-5 w-5 mr-2 text-green-400" />
          SLA & Availability
        </h3>
        <div className="text-slate-400 text-center py-8">
          No SLA data available
        </div>
      </div>
    );
  }

  const getAvailabilityColor = (percentage) => {
    if (percentage >= 99.9) return 'text-green-400';
    if (percentage >= 99.0) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getAvailabilityStatus = (percentage) => {
    if (percentage >= 99.9) return 'Excellent';
    if (percentage >= 99.0) return 'Good';
    if (percentage >= 95.0) return 'Fair';
    return 'Poor';
  };

  return (
    <div className="dashboard-card">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
        <Target className="h-5 w-5 mr-2 text-green-400" />
        SLA & Availability
      </h3>

      {/* Main Availability Metric */}
      <div className="text-center mb-6">
        <div className={`metric-value ${getAvailabilityColor(data.availability_percentage)}`}>
          {data.availability_percentage.toFixed(3)}%
        </div>
        <div className="metric-label">Availability</div>
        <div className={`text-sm mt-2 ${getAvailabilityColor(data.availability_percentage)}`}>
          {getAvailabilityStatus(data.availability_percentage)}
        </div>
      </div>

      {/* SLA Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-slate-700/50 rounded-lg p-3">
          <div className="flex items-center text-slate-400 text-xs mb-1">
            <Target className="h-3 w-3 mr-1" />
            SLA Target
          </div>
          <div className="text-white font-semibold">{data.sla_target}%</div>
        </div>
        <div className="bg-slate-700/50 rounded-lg p-3">
          <div className="flex items-center text-slate-400 text-xs mb-1">
            <Clock className="h-3 w-3 mr-1" />
            MTTR
          </div>
          <div className="text-white font-semibold">{data.mttr_minutes} min</div>
        </div>
      </div>

      {/* Additional Metrics */}
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-slate-400 text-sm">Downtime (current month)</span>
          <span className="text-white font-medium">{data.downtime_minutes.toFixed(1)} min</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-slate-400 text-sm">Open Incidents</span>
          <span className="text-white font-medium flex items-center">
            {data.incident_count > 0 && (
              <AlertTriangle className="h-3 w-3 mr-1 text-yellow-400" />
            )}
            {data.incident_count}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-slate-400 text-sm">Uptime Percentage</span>
          <span className={`font-medium ${getAvailabilityColor(data.uptime_percentage)}`}>
            {data.uptime_percentage.toFixed(3)}%
          </span>
        </div>
      </div>

      {/* SLA Compliance Indicator */}
      <div className="mt-4 pt-4 border-t border-slate-700">
        <div className="flex items-center justify-between">
          <span className="text-slate-400 text-sm">SLA Compliance</span>
          <div className={`px-2 py-1 rounded text-xs font-medium ${
            data.availability_percentage >= data.sla_target 
              ? 'bg-green-400/20 text-green-400' 
              : 'bg-red-400/20 text-red-400'
          }`}>
            {data.availability_percentage >= data.sla_target ? 'COMPLIANT' : 'NON-COMPLIANT'}
          </div>
        </div>
      </div>

      <div className="mt-4 text-xs text-slate-400 text-center">
        Last updated: {new Date(data.last_updated).toLocaleString()}
      </div>
    </div>
  );
};

export default SLAMetrics;
