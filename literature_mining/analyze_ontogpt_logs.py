#!/usr/bin/env python3
"""
OntoGPT Log Analysis Tool

Analyzes verbose OntoGPT logs to identify:
- LiteLLM cost calculation patterns
- Model info lookup frequency
- Performance bottlenecks
- Token usage patterns
"""

import re
import sys
import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Any
import click


class OntoGPTLogAnalyzer:
    def __init__(self):
        self.patterns = {
            'model_info': re.compile(r'Getting model info for.*'),
            'cost_calc': re.compile(r'Cost calculation.*'),
            'litellm_debug': re.compile(r'DEBUG.*litellm.*'),
            'api_call': re.compile(r'Making API call.*'),
            'token_usage': re.compile(r'tokens.*(\d+)'),
            'model_name': re.compile(r'model.*gpt-[45]'),
            'cost_amount': re.compile(r'\$(\d+\.\d+)'),
            'timestamp': re.compile(r'\d{4}-\d{2}-\d{2}.\d{2}:\d{2}:\d{2}')
        }
    
    def analyze_log(self, log_path: Path) -> Dict[str, Any]:
        """Analyze a single OntoGPT verbose log file."""
        if not log_path.exists():
            return {'error': f'Log file not found: {log_path}'}
        
        with open(log_path, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        analysis = {
            'file': str(log_path),
            'total_lines': len(lines),
            'line_patterns': {},
            'performance_issues': [],
            'litellm_analysis': {},
            'cost_analysis': {},
            'summary': {}
        }
        
        # Count pattern occurrences
        for pattern_name, pattern in self.patterns.items():
            matches = pattern.findall(content)
            analysis['line_patterns'][pattern_name] = len(matches)
        
        # Analyze LiteLLM behavior
        analysis['litellm_analysis'] = self._analyze_litellm_patterns(lines)
        
        # Analyze cost calculation patterns
        analysis['cost_analysis'] = self._analyze_cost_patterns(lines)
        
        # Identify performance issues
        analysis['performance_issues'] = self._identify_performance_issues(analysis)
        
        # Generate summary
        analysis['summary'] = self._generate_summary(analysis)
        
        return analysis
    
    def _analyze_litellm_patterns(self, lines: List[str]) -> Dict[str, Any]:
        """Analyze LiteLLM specific patterns."""
        litellm_lines = [line for line in lines if 'litellm' in line.lower()]
        
        model_info_calls = []
        debug_messages = []
        
        for line in litellm_lines:
            if 'getting model info' in line.lower():
                model_info_calls.append(line)
            elif 'DEBUG' in line:
                debug_messages.append(line)
        
        # Find redundant model info calls
        model_patterns = Counter()
        for call in model_info_calls:
            # Extract model name from call
            if 'gpt-5' in call:
                model_patterns['gpt-5'] += 1
            elif 'gpt-4' in call:
                model_patterns['gpt-4'] += 1
        
        return {
            'total_litellm_lines': len(litellm_lines),
            'model_info_calls': len(model_info_calls),
            'debug_messages': len(debug_messages),
            'model_call_frequency': dict(model_patterns),
            'redundant_calls': {model: count for model, count in model_patterns.items() if count > 1}
        }
    
    def _analyze_cost_patterns(self, lines: List[str]) -> Dict[str, Any]:
        """Analyze cost calculation patterns."""
        cost_lines = [line for line in lines if 'cost' in line.lower()]
        
        cost_calculations = []
        total_cost = 0.0
        
        for line in cost_lines:
            cost_match = self.patterns['cost_amount'].search(line)
            if cost_match:
                amount = float(cost_match.group(1))
                total_cost += amount
                cost_calculations.append({
                    'line': line.strip(),
                    'amount': amount
                })
        
        return {
            'total_cost_lines': len(cost_lines),
            'cost_calculations': len(cost_calculations),
            'total_estimated_cost': round(total_cost, 4),
            'cost_per_calculation': round(total_cost / max(len(cost_calculations), 1), 4)
        }
    
    def _identify_performance_issues(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify potential performance issues."""
        issues = []
        
        # Check for excessive model info calls
        litellm = analysis['litellm_analysis']
        if litellm['model_info_calls'] > 10:
            issues.append(f"Excessive model info calls: {litellm['model_info_calls']} (should be cached)")
        
        # Check for redundant calls
        redundant = litellm.get('redundant_calls', {})
        for model, count in redundant.items():
            if count > 5:
                issues.append(f"Redundant {model} model info calls: {count} times")
        
        # Check for excessive debug output
        if litellm['debug_messages'] > 100:
            issues.append(f"Excessive debug messages: {litellm['debug_messages']} lines")
        
        # Check for inefficient cost calculations
        cost = analysis['cost_analysis']
        if cost['cost_calculations'] > 20:
            issues.append(f"Many cost calculations: {cost['cost_calculations']} (possible inefficiency)")
        
        return issues
    
    def _generate_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis summary."""
        return {
            'log_efficiency': 'Poor' if len(analysis['performance_issues']) > 2 else 'Good',
            'main_issues': analysis['performance_issues'][:3],
            'litellm_overhead': analysis['litellm_analysis']['total_litellm_lines'],
            'cost_overhead': analysis['cost_analysis']['total_cost_lines'],
            'recommendations': self._generate_recommendations(analysis)
        }
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        litellm = analysis['litellm_analysis']
        
        if litellm['model_info_calls'] > 5:
            recommendations.append("Consider caching model info to reduce API calls")
        
        if litellm['debug_messages'] > 50:
            recommendations.append("Reduce LiteLLM debug verbosity for production runs")
        
        if analysis['cost_analysis']['cost_calculations'] > 10:
            recommendations.append("Optimize cost calculation frequency")
        
        if not recommendations:
            recommendations.append("Log analysis shows efficient operation")
        
        return recommendations


@click.command()
@click.argument('log_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Output analysis file')
def analyze_log(log_file, output):
    """Analyze OntoGPT verbose log for performance patterns."""
    
    analyzer = OntoGPTLogAnalyzer()
    analysis = analyzer.analyze_log(log_file)
    
    # Print summary
    print("OntoGPT Log Analysis")
    print("=" * 50)
    print(f"File: {analysis['file']}")
    print(f"Total lines: {analysis['total_lines']}")
    print(f"Efficiency: {analysis['summary']['log_efficiency']}")
    
    print("\nLiteLLM Analysis:")
    litellm = analysis['litellm_analysis']
    print(f"  Model info calls: {litellm['model_info_calls']}")
    print(f"  Debug messages: {litellm['debug_messages']}")
    print(f"  Redundant calls: {litellm['redundant_calls']}")
    
    print("\nCost Analysis:")
    cost = analysis['cost_analysis']
    print(f"  Cost calculations: {cost['cost_calculations']}")
    print(f"  Estimated total cost: ${cost['total_estimated_cost']}")
    
    if analysis['performance_issues']:
        print("\nPerformance Issues:")
        for issue in analysis['performance_issues']:
            print(f"  ⚠️  {issue}")
    
    print("\nRecommendations:")
    for rec in analysis['summary']['recommendations']:
        print(f"  💡 {rec}")
    
    if output:
        with open(output, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"\nDetailed analysis saved to: {output}")


if __name__ == '__main__':
    analyze_log()