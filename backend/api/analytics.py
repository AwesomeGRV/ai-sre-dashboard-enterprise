import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import statistics

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    """Advanced analytics and reporting engine"""
    
    def __init__(self):
        self.raw_metrics = []
        self.incident_data = []
        self.alert_data = []
        
    def add_metrics_data(self, metrics: Dict[str, Any]) -> None:
        """Add metrics data for analytics"""
        self.raw_metrics.append(metrics)
        if len(self.raw_metrics) > 1000:
            self.raw_metrics.pop(0)
    
    def add_incident_data(self, incident: Dict[str, Any]) -> None:
        """Add incident data for analytics"""
        self.incident_data.append(incident)
        if len(self.incident_data) > 500:
            self.incident_data.pop(0)
    
    def generate_performance_report(self, time_range: str = "24h") -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.raw_metrics:
            return {"error": "No metrics data available"}
        
        # Filter metrics by time range
        filtered_metrics = self._filter_by_time_range(self.raw_metrics, time_range)
        
        if not filtered_metrics:
            return {"error": "No data in specified time range"}
        
        # Calculate performance metrics
        request_counts = [m.get('request_count', 0) for m in filtered_metrics]
        error_counts = [m.get('error_count', 0) for m in filtered_metrics]
        response_times = [m.get('response_time_avg', 0) for m in filtered_metrics]
        availability_scores = [m.get('availability_percentage', 100) for m in filtered_metrics]
        
        report = {
            "report_period": time_range,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_requests": sum(request_counts),
                "total_errors": sum(error_counts),
                "overall_availability": statistics.mean(availability_scores) if availability_scores else 100,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0
            },
            "trends": {
                "error_rate_trend": self._calculate_trend(error_counts),
                "response_time_trend": self._calculate_trend(response_times),
                "availability_trend": self._calculate_trend(availability_scores)
            },
            "performance_distribution": {
                "excellent_performers": len([r for r in response_times if r < 100]),
                "good_performers": len([r for r in response_times if 100 <= r < 500]),
                "slow_performers": len([r for r in response_times if r >= 500])
            },
            "recommendations": self._generate_performance_recommendations(
                statistics.mean(error_counts), 
                statistics.mean(response_times) if response_times else 0,
                statistics.mean(availability_scores) if availability_scores else 100
            )
        }
        
        return report
    
    def generate_incident_report(self, time_range: str = "7d") -> Dict[str, Any]:
        """Generate incident analysis report"""
        if not self.incident_data:
            return {"error": "No incident data available"}
        
        filtered_incidents = self._filter_incidents_by_time_range(self.incident_data, time_range)
        
        # Analyze incident patterns
        severity_counts = {}
        for incident in filtered_incidents:
            severity = incident.get('severity', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Calculate MTTR
        resolved_incidents = [i for i in filtered_incidents if i.get('status') == 'resolved']
        mttr_values = []
        
        for incident in resolved_incidents:
            if incident.get('created_at') and incident.get('resolved_at'):
                created = datetime.fromisoformat(incident['created_at'])
                resolved = datetime.fromisoformat(incident['resolved_at'])
                mttr_minutes = (resolved - created).total_seconds() / 60
                mttr_values.append(mttr_minutes)
        
        report = {
            "report_period": time_range,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_incidents": len(filtered_incidents),
                "resolved_incidents": len(resolved_incidents),
                "active_incidents": len([i for i in filtered_incidents if i.get('status') == 'open']),
                "mttr_minutes": statistics.mean(mttr_values) if mttr_values else 0,
                "mttr_95th_percentile": statistics.quantiles(mttr_values, 0.95) if len(mttr_values) > 1 else 0
            },
            "severity_breakdown": severity_counts,
            "incident_trends": {
                "daily_incident_count": self._calculate_daily_incident_trend(filtered_incidents),
                "most_common_severity": max(severity_counts, key=severity_counts.get) if severity_counts else 'medium',
                "incident_rate_per_day": len(filtered_incidents) / max(1, self._get_days_in_period(time_range))
            },
            "root_cause_analysis": self._analyze_root_causes(filtered_incidents),
            "recommendations": self._generate_incident_recommendations(severity_counts, len(filtered_incidents))
        }
        
        return report
    
    def generate_sla_report(self, time_range: str = "30d") -> Dict[str, Any]:
        """Generate SLA compliance report"""
        if not self.raw_metrics:
            return {"error": "No metrics data available"}
        
        filtered_metrics = self._filter_by_time_range(self.raw_metrics, time_range)
        
        # Calculate SLA metrics
        availability_scores = [m.get('availability_percentage', 100) for m in filtered_metrics]
        error_rates = [(m.get('error_count', 0) / max(m.get('request_count', 1), 1)) * 100 
                       for m in filtered_metrics]
        
        sla_target = 99.9
        compliance_periods = len([a for a in availability_scores if a >= sla_target])
        total_periods = len(availability_scores)
        
        report = {
            "report_period": time_range,
            "generated_at": datetime.now().isoformat(),
            "sla_summary": {
                "target_availability": sla_target,
                "actual_availability": statistics.mean(availability_scores) if availability_scores else 100,
                "sla_compliance_percentage": (compliance_periods / total_periods * 100) if total_periods > 0 else 0,
                "total_downtime_minutes": sum([(100 - a) * 0.1 for a in availability_scores]),  # Convert to minutes
                "average_error_rate": statistics.mean(error_rates) if error_rates else 0
            },
            "sla_breaches": {
                "total_breaches": total_periods - compliance_periods,
                "worst_availability": min(availability_scores) if availability_scores else 100,
                "breach_details": self._identify_sla_breaches(availability_scores, sla_target)
            },
            "trend_analysis": {
                "availability_trend": self._calculate_trend(availability_scores),
                "error_rate_trend": self._calculate_trend(error_rates)
            },
            "recommendations": self._generate_sla_recommendations(
                statistics.mean(availability_scores) if availability_scores else 100,
                sla_target,
                total_periods - compliance_periods
            )
        }
        
        return report
    
    def generate_capacity_planning_report(self) -> Dict[str, Any]:
        """Generate capacity planning recommendations"""
        if not self.raw_metrics:
            return {"error": "No metrics data available"}
        
        # Analyze current capacity usage
        recent_metrics = self.raw_metrics[-24:] if len(self.raw_metrics) >= 24 else self.raw_metrics
        
        request_counts = [m.get('request_count', 0) for m in recent_metrics]
        response_times = [m.get('response_time_avg', 0) for m in recent_metrics]
        error_rates = [(m.get('error_count', 0) / max(m.get('request_count', 1), 1)) * 100 
                     for m in recent_metrics]
        
        # Calculate growth trends
        request_growth = self._calculate_growth_trend(request_counts)
        peak_usage = {
            "max_requests_per_minute": max(request_counts) if request_counts else 0,
            "peak_response_time": max(response_times) if response_times else 0,
            "peak_error_rate": max(error_rates) if error_rates else 0
        }
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "current_capacity_analysis": {
                "avg_requests_per_period": statistics.mean(request_counts) if request_counts else 0,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "avg_error_rate": statistics.mean(error_rates) if error_rates else 0,
                "utilization_percentage": min(95, (statistics.mean(request_counts) / 1000) * 100)  # Assuming 1000 as baseline
            },
            "growth_analysis": {
                "request_growth_rate": request_growth,
                "trend_direction": "increasing" if request_growth > 0.1 else "stable" if request_growth > -0.1 else "decreasing"
            },
            "peak_usage_analysis": peak_usage,
            "capacity_recommendations": {
                "scaling_needed": request_growth > 0.2 or statistics.mean(response_times) > 500,
                "recommended_capacity": int(statistics.mean(request_counts) * 1.5) if request_counts else 1000,
                "performance_optimization": statistics.mean(response_times) > 300,
                "monitoring_enhancement": statistics.mean(error_rates) > 1.0
            },
            "infrastructure_suggestions": self._generate_infrastructure_recommendations(
                statistics.mean(request_counts) if request_counts else 0,
                statistics.mean(response_times) if response_times else 0
            )
        }
        
        return report
    
    def _filter_by_time_range(self, metrics: List[Dict], time_range: str) -> List[Dict]:
        """Filter metrics by time range"""
        if not metrics:
            return []
        
        # Parse time range (e.g., "24h", "7d", "30d")
        if time_range.endswith('h'):
            hours = int(time_range[:-1])
            cutoff_time = datetime.now() - timedelta(hours=hours)
        elif time_range.endswith('d'):
            days = int(time_range[:-1])
            cutoff_time = datetime.now() - timedelta(days=days)
        else:
            cutoff_time = datetime.now() - timedelta(days=1)  # Default to 1 day
        
        return [m for m in metrics if datetime.fromisoformat(m['timestamp']) >= cutoff_time]
    
    def _filter_incidents_by_time_range(self, incidents: List[Dict], time_range: str) -> List[Dict]:
        """Filter incidents by time range"""
        if not incidents:
            return []
        
        if time_range.endswith('h'):
            hours = int(time_range[:-1])
            cutoff_time = datetime.now() - timedelta(hours=hours)
        elif time_range.endswith('d'):
            days = int(time_range[:-1])
            cutoff_time = datetime.now() - timedelta(days=days)
        else:
            cutoff_time = datetime.now() - timedelta(days=1)
        
        return [i for i in incidents if datetime.fromisoformat(i['created_at']) >= cutoff_time]
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return "insufficient_data"
        
        recent_avg = statistics.mean(values[-5:]) if len(values) >= 5 else statistics.mean(values)
        older_avg = statistics.mean(values[-10:-5]) if len(values) >= 10 else statistics.mean(values[:-5])
        
        if recent_avg > older_avg * 1.1:
            return "increasing"
        elif recent_avg < older_avg * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_growth_trend(self, values: List[int]) -> float:
        """Calculate growth rate as percentage"""
        if len(values) < 2:
            return 0.0
        
        recent_avg = statistics.mean(values[-7:]) if len(values) >= 7 else statistics.mean(values)
        older_avg = statistics.mean(values[-14:-7]) if len(values) >= 14 else statistics.mean(values[:-7])
        
        if older_avg == 0:
            return 0.0
        
        return ((recent_avg - older_avg) / older_avg) * 100
    
    def _get_days_in_period(self, time_range: str) -> int:
        """Get number of days in time range"""
        if time_range.endswith('h'):
            hours = int(time_range[:-1])
            return max(1, hours // 24)
        elif time_range.endswith('d'):
            return int(time_range[:-1])
        else:
            return 1
    
    def _identify_sla_breaches(self, availability_scores: List[float], target: float) -> List[Dict]:
        """Identify specific SLA breaches"""
        breaches = []
        for i, availability in enumerate(availability_scores):
            if availability < target:
                breaches.append({
                    "period_index": i,
                    "availability": availability,
                    "shortfall_percentage": target - availability
                })
        return breaches
    
    def _generate_performance_recommendations(self, avg_errors: float, avg_response_time: float, avg_availability: float) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        if avg_errors > 5:
            recommendations.append("Investigate root cause of high error rate")
        
        if avg_response_time > 500:
            recommendations.append("Optimize application performance and database queries")
        
        if avg_availability < 99.5:
            recommendations.append("Implement high availability and failover mechanisms")
        
        if avg_response_time > 200:
            recommendations.append("Consider implementing caching strategies")
        
        return recommendations
    
    def _generate_incident_recommendations(self, severity_counts: Dict, total_incidents: int) -> List[str]:
        """Generate incident management recommendations"""
        recommendations = []
        
        if severity_counts.get('critical', 0) > 0:
            recommendations.append("Review critical incident response procedures")
        
        if total_incidents > 10:
            recommendations.append("Implement proactive monitoring to prevent incidents")
        
        if severity_counts.get('high', 0) > severity_counts.get('medium', 0):
            recommendations.append("Focus on reducing high-severity incidents")
        
        return recommendations
    
    def _generate_sla_recommendations(self, actual_availability: float, target: float, breaches: int) -> List[str]:
        """Generate SLA improvement recommendations"""
        recommendations = []
        
        if actual_availability < target:
            recommendations.append(f"Improve availability by {target - actual_availability:.2f}% to meet SLA")
        
        if breaches > 2:
            recommendations.append("Review and improve incident response procedures")
        
        if actual_availability < 99.5:
            recommendations.append("Implement redundant systems and load balancing")
        
        return recommendations
    
    def _analyze_root_causes(self, incidents: List[Dict]) -> Dict[str, Any]:
        """Analyze root causes from incident data"""
        # This is a simplified analysis - in production, would use AI/ML
        causes = {}
        for incident in incidents:
            title = incident.get('title', '').lower()
            if 'database' in title or 'db' in title:
                causes['database'] = causes.get('database', 0) + 1
            elif 'network' in title or 'connection' in title:
                causes['network'] = causes.get('network', 0) + 1
            elif 'memory' in title or 'cpu' in title:
                causes['infrastructure'] = causes.get('infrastructure', 0) + 1
        
        return causes
    
    def _generate_infrastructure_recommendations(self, avg_requests: int, avg_response_time: float) -> List[str]:
        """Generate infrastructure scaling recommendations"""
        recommendations = []
        
        if avg_requests > 800:
            recommendations.append("Consider horizontal scaling with load balancer")
        
        if avg_response_time > 300:
            recommendations.append("Upgrade CPU or optimize application code")
        
        if avg_requests > 500 and avg_response_time > 200:
            recommendations.append("Implement auto-scaling based on metrics")
        
        return recommendations

# Global analytics engine instance
analytics_engine = AnalyticsEngine()
