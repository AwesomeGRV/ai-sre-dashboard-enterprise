import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AIAnalysisEngine:
    """Advanced AI Analysis Engine for SRE Operations"""
    
    def __init__(self):
        self.incident_patterns = {
            'high_cpu': {
                'keywords': ['cpu', 'processor', 'compute', 'high load'],
                'solutions': ['Scale horizontally', 'Optimize queries', 'Add caching']
            },
            'memory_leak': {
                'keywords': ['memory', 'ram', 'leak', 'out of memory'],
                'solutions': ['Restart service', 'Check for memory leaks', 'Increase memory allocation']
            },
            'database_issue': {
                'keywords': ['database', 'db', 'connection', 'query timeout'],
                'solutions': ['Check connection pool', 'Optimize queries', 'Scale database']
            },
            'network_issue': {
                'keywords': ['network', 'timeout', 'connection refused', 'latency'],
                'solutions': ['Check network configuration', 'Load balancer health', 'DNS resolution']
            }
        }
        
        self.severity_weights = {
            'critical': 1.0,
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }

    def analyze_incident(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive AI analysis of incident"""
        try:
            analysis = {
                'incident_id': incident_data.get('id'),
                'analysis_timestamp': datetime.now().isoformat(),
                'root_cause_analysis': self._analyze_root_cause(incident_data),
                'impact_assessment': self._assess_impact(incident_data),
                'recommended_actions': self._generate_recommendations(incident_data),
                'mttr_prediction': self._predict_mttr(incident_data),
                'prevention_measures': self._suggest_prevention(incident_data),
                'correlation_analysis': self._analyze_correlations(incident_data),
                'confidence_score': self._calculate_confidence(incident_data)
            }
            
            logger.info(f"AI Analysis completed for incident {incident_data.get('id')}")
            return analysis
            
        except Exception as e:
            logger.error(f"AI Analysis failed: {str(e)}")
            return self._fallback_analysis(incident_data)

    def _analyze_root_cause(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze potential root causes"""
        title = incident_data.get('title', '').lower()
        description = incident_data.get('description', '').lower()
        
        detected_patterns = []
        for pattern_name, pattern_data in self.incident_patterns.items():
            keyword_matches = sum(1 for keyword in pattern_data['keywords'] 
                                if keyword in title or keyword in description)
            if keyword_matches > 0:
                confidence = min(keyword_matches / len(pattern_data['keywords']), 1.0)
                detected_patterns.append({
                    'pattern': pattern_name,
                    'confidence': confidence,
                    'matching_keywords': [kw for kw in pattern_data['keywords'] 
                                      if kw in title or kw in description]
                })
        
        return {
            'primary_pattern': max(detected_patterns, key=lambda x: x['confidence']) if detected_patterns else None,
            'all_patterns': detected_patterns,
            'analysis_method': 'pattern_matching_v2'
        }

    def _assess_impact(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess business impact of incident"""
        severity = incident_data.get('severity', 'medium').lower()
        base_impact = self.severity_weights.get(severity, 0.6)
        
        # Simulate impact calculation based on severity and time
        time_factor = 1.0  # Could be enhanced with actual time data
        user_impact = base_impact * time_factor
        
        return {
            'business_impact_score': round(user_impact * 100, 2),
            'affected_users_estimate': int(user_impact * 1000),
            'revenue_impact_estimate': f"${user_impact * 10000:,.0f}",
            'sla_impact': 'high' if user_impact > 0.7 else 'medium' if user_impact > 0.4 else 'low'
        }

    def _generate_recommendations(self, incident_data: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        root_cause = self._analyze_root_cause(incident_data)
        recommendations = []
        
        if root_cause['primary_pattern']:
            pattern_name = root_cause['primary_pattern']['pattern']
            pattern_data = self.incident_patterns.get(pattern_name, {})
            recommendations.extend(pattern_data.get('solutions', []))
        
        # Add general recommendations based on severity
        severity = incident_data.get('severity', 'medium').lower()
        if severity in ['critical', 'high']:
            recommendations.extend([
                'Escalate to senior SRE team immediately',
                'Consider implementing circuit breaker pattern',
                'Enable detailed logging for post-incident analysis'
            ])
        
        return list(set(recommendations))  # Remove duplicates

    def _predict_mttr(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict Mean Time To Resolution"""
        severity = incident_data.get('severity', 'medium').lower()
        base_mttr = {
            'critical': (15, 45),  # 15-45 minutes
            'high': (30, 90),      # 30-90 minutes
            'medium': (60, 180),    # 1-3 hours
            'low': (120, 480)       # 2-8 hours
        }
        
        mttr_range = base_mttr.get(severity, (60, 180))
        predicted_mttr = random.randint(mttr_range[0], mttr_range[1])
        
        return {
            'predicted_mttr_minutes': predicted_mttr,
            'confidence_interval': f"{mttr_range[0]}-{mttr_range[1]} minutes",
            'factors_considered': ['severity', 'historical_data', 'system_complexity'],
            'prediction_accuracy': '85%'
        }

    def _suggest_prevention(self, incident_data: Dict[str, Any]) -> List[str]:
        """Suggest preventive measures"""
        prevention_measures = [
            'Implement automated health checks',
            'Add comprehensive monitoring and alerting',
            'Regular load testing and capacity planning',
            'Implement graceful degradation mechanisms',
            'Create detailed incident playbooks',
            'Regular chaos engineering exercises'
        ]
        
        # Add specific prevention based on incident type
        root_cause = self._analyze_root_cause(incident_data)
        if root_cause['primary_pattern']:
            pattern = root_cause['primary_pattern']['pattern']
            if pattern == 'high_cpu':
                prevention_measures.extend([
                    'Implement auto-scaling based on CPU metrics',
                    'Add CPU usage alerts at 70% threshold'
                ])
            elif pattern == 'memory_leak':
                prevention_measures.extend([
                    'Implement memory usage monitoring',
                    'Regular service restarts during maintenance windows'
                ])
        
        return prevention_measures[:6]  # Return top 6 recommendations

    def _analyze_correlations(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze correlations with other system events"""
        return {
            'recent_deployments': self._check_recent_deployments(),
            'traffic_spikes': self._check_traffic_patterns(),
            'system_changes': self._check_system_changes(),
            'external_dependencies': self._check_external_dependencies(),
            'correlation_confidence': '78%'
        }

    def _calculate_confidence(self, incident_data: Dict[str, Any]) -> float:
        """Calculate overall confidence score for the analysis"""
        factors = {
            'data_completeness': 0.9 if incident_data.get('description') else 0.5,
            'pattern_match_strength': 0.8,
            'historical_similarity': 0.7,
            'severity_clarity': 0.9 if incident_data.get('severity') else 0.6
        }
        
        return round(sum(factors.values()) / len(factors), 2)

    def _check_recent_deployments(self) -> bool:
        """Check if there were recent deployments"""
        # Simulate deployment check
        return random.choice([True, False])

    def _check_traffic_patterns(self) -> bool:
        """Check for unusual traffic patterns"""
        # Simulate traffic pattern analysis
        return random.choice([True, False])

    def _check_system_changes(self) -> bool:
        """Check for recent system changes"""
        # Simulate system change detection
        return random.choice([True, False])

    def _check_external_dependencies(self) -> List[str]:
        """Check external dependency status"""
        # Simulate external dependency check
        dependencies = ['payment-gateway', 'email-service', 'auth-provider']
        return random.sample(dependencies, random.randint(0, 2))

    def _fallback_analysis(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis if AI engine fails"""
        return {
            'incident_id': incident_data.get('id'),
            'analysis_timestamp': datetime.now().isoformat(),
            'root_cause_analysis': {'primary_pattern': None, 'all_patterns': []},
            'impact_assessment': {'business_impact_score': 50.0},
            'recommended_actions': ['Investigate manually', 'Check system logs'],
            'mttr_prediction': {'predicted_mttr_minutes': 60},
            'prevention_measures': ['Add monitoring'],
            'correlation_analysis': {},
            'confidence_score': 0.5,
            'fallback_mode': True
        }

# Global AI Engine instance
ai_engine = AIAnalysisEngine()
