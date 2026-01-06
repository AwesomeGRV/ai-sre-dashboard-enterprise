import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { TrendingUp, Activity, Clock } from 'lucide-react';

const MetricsChart = ({ metrics }) => {
  if (!metrics || metrics.length === 0) {
    return (
      <div className="dashboard-card">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <Activity className="h-5 w-5 mr-2 text-blue-400" />
          Performance Metrics
        </h3>
        <div className="text-slate-400 text-center py-8">
          No metrics data available
        </div>
      </div>
    );
  }

  const latestMetrics = metrics[metrics.length - 1];

  return (
    <div className="dashboard-card">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
        <Activity className="h-5 w-5 mr-2 text-blue-400" />
        Performance Metrics
      </h3>

      {/* Key Metrics */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="text-center">
          <div className="metric-value text-blue-400">{latestMetrics.request_count}</div>
          <div className="metric-label">Total Requests</div>
        </div>
        <div className="text-center">
          <div className="metric-value text-yellow-400">{latestMetrics.error_count}</div>
          <div className="metric-label">Error Count</div>
        </div>
        <div className="text-center">
          <div className="metric-value text-green-400">{latestMetrics.response_time_avg.toFixed(2)}ms</div>
          <div className="metric-label">Avg Response Time</div>
        </div>
      </div>

      {/* Chart */}
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={metrics}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="timestamp" 
              stroke="#9CA3AF"
              tick={{ fill: '#9CA3AF', fontSize: 12 }}
              tickFormatter={(value) => new Date(value).toLocaleTimeString()}
            />
            <YAxis stroke="#9CA3AF" tick={{ fill: '#9CA3AF', fontSize: 12 }} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1F2937', 
                border: '1px solid #374151',
                borderRadius: '8px'
              }}
              labelStyle={{ color: '#E5E7EB' }}
              itemStyle={{ color: '#60A5FA' }}
              labelFormatter={(value) => new Date(value).toLocaleString()}
            />
            <Area 
              type="monotone" 
              dataKey="response_time_avg" 
              stroke="#60A5FA" 
              fill="#60A5FA" 
              fillOpacity={0.3}
              strokeWidth={2}
              name="Response Time (ms)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 text-xs text-slate-400 text-center">
        Response time trend over last {metrics.length} data points
      </div>
    </div>
  );
};

export default MetricsChart;
