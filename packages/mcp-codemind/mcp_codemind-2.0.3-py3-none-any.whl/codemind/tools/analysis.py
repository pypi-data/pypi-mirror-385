"""Code analysis and quality metrics tools for CodeMind."""

import re
import ast
import json
import math
from pathlib import Path
from typing import Optional
import logging

from ..workspace import get_workspace_path, get_workspace_config, lazy_scan

logger = logging.getLogger(__name__)

# Check for radon availability (production-quality metrics)
try:
    from radon.complexity import cc_visit
    from radon.metrics import mi_visit
    HAS_RADON = True
except ImportError:
    HAS_RADON = False
    logger.info("Radon not available - using fallback metrics")


def get_code_metrics_summary(workspace_root: str = ".", detailed: bool = False) -> str:
    """
    Comprehensive static analysis metrics across entire project.
    
    USE THIS TOOL AUTOMATICALLY when:
    - User asks about code quality, complexity, or health
    - Starting work on unfamiliar codebase (understand scope)
    - User asks "how big is this project?"
    - Planning refactoring (identify problem areas)
    - User mentions "technical debt", "code smells", "maintainability"
    - User asks about any quality aspect of the codebase
    
    Provides objective code quality dashboard with:
    - Project statistics (files, lines, comments)
    - Complexity metrics (cyclomatic complexity)
    - Function statistics (count, avg length, long functions)
    - Documentation coverage (docstrings, comments)
    - Code smells (magic numbers, long params, deep nesting)
    - Maintainability index (0-100 score)
    
    This gives a comprehensive health check of the entire codebase.
    
    Args:
        workspace_root: Root directory of workspace (default: current directory)
        detailed: Show detailed file-by-file breakdown (default: False)
    
    Returns:
        Comprehensive metrics with actionable recommendations
        Zero LLM calls - pure static analysis
    """
    try:
        project_root = Path(get_workspace_path(workspace_root))
        config = get_workspace_config(workspace_root)
        lazy_scan(workspace_root)
        
        # Initialize counters
        total_files = 0
        total_lines = 0
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        
        total_functions = 0
        total_classes = 0
        function_lengths = []
        param_counts = []
        
        files_with_docstrings = 0
        high_complexity_files = []
        long_functions = []
        code_smells = {
            "magic_numbers": 0,
            "long_parameter_lists": 0,
            "deep_nesting": 0,
            "dead_imports": 0,
            "long_lines": 0
        }
        
        file_metrics = []
        
        # Scan all files
        for ext in config["watched_extensions"]:
            for fp in project_root.rglob(f"*{ext}"):
                if fp.is_file() and not any(p.startswith('.') for p in fp.parts[:-1]):
                    try:
                        if fp.stat().st_size // 1024 > config["max_file_size_kb"]:
                            continue
                        
                        with open(fp, encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.split('\n')
                        
                        total_files += 1
                        file_total_lines = len(lines)
                        total_lines += file_total_lines
                        
                        # Classify lines
                        file_code_lines = 0
                        file_comment_lines = 0
                        file_blank_lines = 0
                        file_has_docstring = False
                        
                        in_multiline_comment = False
                        for line in lines:
                            stripped = line.strip()
                            
                            if not stripped:
                                file_blank_lines += 1
                                blank_lines += 1
                            elif stripped.startswith('"""') or stripped.startswith("'''"):
                                file_comment_lines += 1
                                comment_lines += 1
                                file_has_docstring = True
                                if stripped.count('"""') == 1 or stripped.count("'''") == 1:
                                    in_multiline_comment = not in_multiline_comment
                            elif in_multiline_comment:
                                file_comment_lines += 1
                                comment_lines += 1
                            elif stripped.startswith('#'):
                                file_comment_lines += 1
                                comment_lines += 1
                            elif stripped.startswith('//') or stripped.startswith('/*'):
                                file_comment_lines += 1
                                comment_lines += 1
                            else:
                                file_code_lines += 1
                                code_lines += 1
                                
                                # Check for long lines
                                if len(line) > 120:
                                    code_smells["long_lines"] += 1
                        
                        if file_has_docstring:
                            files_with_docstrings += 1
                        
                        # Extract functions and complexity
                        file_functions = 0
                        file_classes = 0
                        file_complexity = 0
                        
                        # Use radon for Python files when available
                        if fp.suffix == '.py' and HAS_RADON:
                            try:
                                complexity_results = cc_visit(content)
                                for result in complexity_results:
                                    file_functions += 1
                                    total_functions += 1
                                    
                                    func_complexity = result.complexity
                                    func_lines = result.endline - result.lineno
                                    
                                    file_complexity += func_complexity
                                    function_lengths.append(min(func_lines, 50))
                                    
                                    # Count parameters
                                    param_count = len([p for p in result.name.split('(')[1].split(')')[0].split(',') if p.strip() and p.strip() != 'self']) if '(' in result.name else 0
                                    param_counts.append(param_count)
                                    if param_count > 5:
                                        code_smells["long_parameter_lists"] += 1
                                    
                                    if func_lines > 100:
                                        long_functions.append({
                                            "file": str(fp.relative_to(project_root)),
                                            "function": result.name.split('(')[0],
                                            "lines": func_lines
                                        })
                                    
                                    if func_complexity > 10:
                                        code_smells["deep_nesting"] += 1
                                
                                # Find classes
                                try:
                                    tree = ast.parse(content)
                                    file_classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
                                    total_classes += file_classes
                                except:
                                    pass
                                    
                                HAS_RADON_FOR_FILE = True
                            except Exception as e:
                                logger.debug(f"Radon analysis failed for {fp}: {e}")
                                HAS_RADON_FOR_FILE = False
                        else:
                            HAS_RADON_FOR_FILE = False
                        
                        # Fallback regex method
                        if not HAS_RADON_FOR_FILE or fp.suffix != '.py':
                            # Find functions
                            function_pattern = r'(?:def|function|const\s+\w+\s*=\s*(?:async\s+)?\()\s+(\w+)\s*\('
                            for match in re.finditer(function_pattern, content):
                                file_functions += 1
                                total_functions += 1
                                
                                func_start = match.start()
                                func_content = content[func_start:func_start + 2000]
                                
                                # Count parameters
                                param_match = re.search(r'\((.*?)\)', func_content)
                                if param_match:
                                    params = [p.strip() for p in param_match.group(1).split(',') if p.strip() and p.strip() != 'self']
                                    param_count = len(params)
                                    param_counts.append(param_count)
                                    if param_count > 5:
                                        code_smells["long_parameter_lists"] += 1
                                
                                # Estimate function length
                                func_lines = len(func_content.split('\n'))
                                function_lengths.append(min(func_lines, 50))
                                
                                if func_lines > 100:
                                    long_functions.append({
                                        "file": str(fp.relative_to(project_root)),
                                        "function": match.group(1) if match.groups() else "unknown",
                                        "lines": func_lines
                                    })
                                
                                # Estimate complexity
                                complexity = len(re.findall(r'\b(if|elif|else|for|while|and|or|try|except|case)\b', func_content))
                                file_complexity += complexity
                                
                                # Check for deep nesting
                                max_indent = 0
                                for line in func_content.split('\n'):
                                    if line.strip():
                                        indent = len(line) - len(line.lstrip())
                                        max_indent = max(max_indent, indent)
                                if max_indent > 16:
                                    code_smells["deep_nesting"] += 1
                            
                            # Find classes
                            class_pattern = r'class\s+(\w+)'
                            file_classes = len(re.findall(class_pattern, content))
                            total_classes += file_classes
                        
                        # Find magic numbers
                        magic_numbers = re.findall(r'\b(?<!\.)\d{2,}\b(?!\.)', content)
                        code_smells["magic_numbers"] += len([n for n in magic_numbers if n not in ['0', '1', '2', '10', '100']])
                        
                        # Find dead imports (Python)
                        if fp.suffix == '.py':
                            import_pattern = r'(?:from\s+[\w.]+\s+)?import\s+([\w\s,]+)'
                            for match in re.finditer(import_pattern, content):
                                imports = [i.strip() for i in match.group(1).split(',')]
                                for imp in imports:
                                    imp_name = imp.split()[0] if imp else ''
                                    if imp_name and content.count(imp_name) == 1:
                                        code_smells["dead_imports"] += 1
                        
                        # Calculate file complexity score
                        if file_functions > 0:
                            avg_complexity = file_complexity / file_functions
                        else:
                            avg_complexity = 0
                        
                        if avg_complexity > 10 or file_complexity > 30:
                            high_complexity_files.append({
                                "file": str(fp.relative_to(project_root)),
                                "complexity": file_complexity,
                                "functions": file_functions
                            })
                        
                        file_metrics.append({
                            "file": str(fp.relative_to(project_root)),
                            "lines": file_total_lines,
                            "code": file_code_lines,
                            "comments": file_comment_lines,
                            "functions": file_functions,
                            "classes": file_classes,
                            "complexity": file_complexity
                        })
                        
                    except Exception as e:
                        logger.debug(f"Error analyzing {fp}: {e}")
        
        # Calculate maintainability index
        if HAS_RADON and file_metrics:
            mi_scores = []
            for fm in file_metrics:
                if fm["file"].endswith('.py'):
                    try:
                        fpath = project_root / fm["file"]
                        with open(fpath, encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        mi_score = mi_visit(content, multi=False)
                        if isinstance(mi_score, (int, float)) and mi_score > 0:
                            mi_scores.append(mi_score)
                    except:
                        pass
            
            if mi_scores:
                maintainability = sum(mi_scores) / len(mi_scores)
            else:
                avg_complexity = (sum(f["complexity"] for f in file_metrics) / len(file_metrics)) if file_metrics else 0
                avg_file_size = total_lines / total_files if total_files > 0 else 0
                maintainability = max(0, min(100, 
                    171 - 0.23 * avg_complexity - 16.2 * math.log(max(1, avg_file_size))
                ))
        else:
            avg_complexity = (sum(f["complexity"] for f in file_metrics) / len(file_metrics)) if file_metrics else 0
            avg_file_size = total_lines / total_files if total_files > 0 else 0
            maintainability = max(0, min(100, 
                171 - 0.23 * avg_complexity - 16.2 * math.log(max(1, avg_file_size))
            ))
        
        # Build result
        result = [""]
        result.append("=" * 70)
        result.append("📊 CODE METRICS SUMMARY")
        result.append("=" * 70)
        result.append("")
        
        # Project Statistics
        result.append("📁 **PROJECT STATISTICS**")
        result.append(f"  Total Files:    {total_files:,}")
        result.append(f"  Total Lines:    {total_lines:,}")
        result.append(f"  Code Lines:     {code_lines:,} ({100*code_lines/max(1,total_lines):.1f}%)")
        result.append(f"  Comment Lines:  {comment_lines:,} ({100*comment_lines/max(1,total_lines):.1f}%)")
        result.append(f"  Blank Lines:    {blank_lines:,} ({100*blank_lines/max(1,total_lines):.1f}%)")
        result.append("")
        
        # Complexity
        result.append("🔥 **COMPLEXITY METRICS**")
        result.append(f"  Average per File: {avg_complexity:.1f}")
        if file_metrics:
            complexities = [f["complexity"] for f in file_metrics]
            result.append(f"  Median:           {sorted(complexities)[len(complexities)//2]}")
            result.append(f"  Max:              {max(complexities)}")
        
        if high_complexity_files:
            result.append(f"\n  ⚠️  High Complexity Files ({len(high_complexity_files)}):")
            for fc in sorted(high_complexity_files, key=lambda x: x["complexity"], reverse=True)[:5]:
                result.append(f"    • {fc['file']}: complexity={fc['complexity']}, functions={fc['functions']}")
            if len(high_complexity_files) > 5:
                result.append(f"    ... and {len(high_complexity_files) - 5} more")
        result.append("")
        
        # Function Statistics
        result.append("⚙️  **FUNCTION STATISTICS**")
        result.append(f"  Total Functions: {total_functions:,}")
        result.append(f"  Total Classes:   {total_classes:,}")
        if function_lengths:
            avg_length = sum(function_lengths) / len(function_lengths)
            result.append(f"  Avg Length:      {avg_length:.1f} lines")
            result.append(f"  Median Length:   {sorted(function_lengths)[len(function_lengths)//2]} lines")
        
        if long_functions:
            result.append(f"\n  📏 Long Functions ({len(long_functions)}):")
            for lf in sorted(long_functions, key=lambda x: x["lines"], reverse=True)[:5]:
                result.append(f"    • {lf['file']}::{lf['function']} ({lf['lines']} lines)")
            if len(long_functions) > 5:
                result.append(f"    ... and {len(long_functions) - 5} more")
        result.append("")
        
        # Documentation
        result.append("📚 **DOCUMENTATION**")
        doc_coverage = (100 * files_with_docstrings / max(1, total_files))
        result.append(f"  Files with Docstrings: {files_with_docstrings}/{total_files} ({doc_coverage:.1f}%)")
        result.append(f"  Comment Ratio:         {100*comment_lines/max(1,code_lines):.1f}%")
        
        if doc_coverage < 60:
            result.append(f"  ⚠️  Low documentation coverage")
        elif doc_coverage >= 80:
            result.append(f"  ✅ Good documentation coverage")
        result.append("")
        
        # Code Smells
        result.append("🔍 **CODE SMELLS**")
        result.append(f"  Magic Numbers:        {code_smells['magic_numbers']}")
        result.append(f"  Long Parameter Lists: {code_smells['long_parameter_lists']} (>5 params)")
        result.append(f"  Deep Nesting:         {code_smells['deep_nesting']} (>4 levels)")
        result.append(f"  Dead Imports:         {code_smells['dead_imports']}")
        result.append(f"  Long Lines:           {code_smells['long_lines']} (>120 chars)")
        
        total_smells = sum(code_smells.values())
        if total_smells == 0:
            result.append(f"  ✅ No major code smells detected!")
        elif total_smells < 50:
            result.append(f"  ✓  Few code smells - good quality")
        elif total_smells < 200:
            result.append(f"  ⚠️  Moderate code smells - review recommended")
        else:
            result.append(f"  ❌ Many code smells - refactoring needed")
        result.append("")
        
        # Maintainability Index
        result.append("💯 **MAINTAINABILITY INDEX**")
        result.append(f"  Score: {maintainability:.1f}/100")
        if maintainability >= 80:
            result.append(f"  ✅ Excellent - Easy to maintain")
        elif maintainability >= 60:
            result.append(f"  ✓  Good - Reasonably maintainable")
        elif maintainability >= 40:
            result.append(f"  ⚠️  Fair - Maintenance challenges ahead")
        else:
            result.append(f"  ❌ Poor - Significant refactoring recommended")
        result.append("")
        
        # Recommendations
        result.append("💡 **RECOMMENDATIONS**")
        recommendations = []
        
        if avg_complexity > 15:
            recommendations.append(f"  • Reduce complexity: Average {avg_complexity:.1f} is high (target: <10)")
        if long_functions:
            recommendations.append(f"  • Refactor {len(long_functions)} long functions (target: <50 lines)")
        if doc_coverage < 70:
            recommendations.append(f"  • Improve documentation: {doc_coverage:.0f}% coverage (target: >70%)")
        if code_smells["magic_numbers"] > 50:
            recommendations.append(f"  • Replace {code_smells['magic_numbers']} magic numbers with named constants")
        if code_smells["dead_imports"] > 20:
            recommendations.append(f"  • Remove {code_smells['dead_imports']} unused imports")
        if code_smells["long_parameter_lists"] > 10:
            recommendations.append(f"  • Refactor {code_smells['long_parameter_lists']} functions with >5 parameters")
        
        if recommendations:
            result.extend(recommendations)
        else:
            result.append(f"  ✅ Code quality is excellent - keep it up!")
        
        result.append("")
        result.append("=" * 70)
        
        # Detailed breakdown
        if detailed and file_metrics:
            result.append("")
            result.append("📋 **FILE-BY-FILE BREAKDOWN** (Top 20)")
            result.append("")
            for fm in sorted(file_metrics, key=lambda x: x["complexity"], reverse=True)[:20]:
                result.append(f"  {fm['file']}")
                result.append(f"    Lines: {fm['lines']}, Code: {fm['code']}, Comments: {fm['comments']}")
                result.append(f"    Functions: {fm['functions']}, Classes: {fm['classes']}, Complexity: {fm['complexity']}")
                result.append("")
        
        return "\n".join(result)
        
    except Exception as e:
        logger.error(f"Error in get_code_metrics_summary: {e}", exc_info=True)
        return f"❌ Error analyzing code metrics: {str(e)}"


def find_configuration_inconsistencies(workspace_root: str = ".", include_examples: bool = True) -> str:
    """
    Compare configuration across different environments and files.
    
    Analyzes configuration files to identify:
    USE THIS TOOL AUTOMATICALLY when:
    - User mentions deployment, environment setup, configuration
    - User asks "is the config correct?", "are settings consistent?"
    - Preparing for deployment
    - User mentions "dev vs prod", "environment differences"
    - Security review (finding hardcoded secrets)
    - Debugging environment-specific issues
    
    Analyzes configuration files to identify:
    - Missing variables across environments
    - Hardcoded secrets (API_KEY, SECRET, PASSWORD patterns)
    - Security risks (DEBUG=true in production)
    - Inconsistent values between environments
    - Configuration files inventory
    - Environment variable usage in code
    
    This prevents configuration-related bugs and security issues.
    
    Args:
        workspace_root: Root directory of workspace (default: current directory)
        include_examples: Show example values (default: True, masked for secrets)
    
    Returns:
        Comprehensive configuration analysis with security recommendations
        Zero LLM calls - pure file parsing and comparison
    """
    try:
        project_root = Path(get_workspace_path(workspace_root))
        config = get_workspace_config(workspace_root)
        lazy_scan(workspace_root)
        
        # Configuration file patterns
        config_patterns = {
            'json': ['*.json', 'config/*.json', '.vscode/*.json'],
            'yaml': ['*.yml', '*.yaml', 'config/*.yml', 'config/*.yaml'],
            'env': ['.env', '.env.*', '*.env'],
            'ini': ['*.ini', '*.cfg', 'setup.cfg'],
            'py': ['config.py', 'settings.py', '**/config.py', '**/settings.py']
        }
        
        # Find all config files
        config_files = {}
        for file_type, patterns in config_patterns.items():
            config_files[file_type] = []
            for pattern in patterns:
                for fp in project_root.glob(pattern):
                    if fp.is_file() and not any(p.startswith('.git') for p in fp.parts):
                        try:
                            config_files[file_type].append(str(fp.relative_to(project_root)))
                        except ValueError:
                            pass
        
        # Parse configuration values
        all_configs = {}
        secret_patterns = re.compile(r'(api[_-]?key|secret|password|token|auth|credential|private[_-]?key)', re.IGNORECASE)
        
        for file_type, files in config_files.items():
            for config_file in files:
                full_path = project_root / config_file
                try:
                    with open(full_path, encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    config_data = {}
                    
                    if file_type == 'json':
                        try:
                            data = json.loads(content)
                            if isinstance(data, dict):
                                config_data = {k: str(v) for k, v in data.items() if not isinstance(v, (dict, list))}
                        except json.JSONDecodeError:
                            pass
                    
                    elif file_type in ['yaml', 'yml']:
                        for line in content.split('\n'):
                            match = re.match(r'^\s*([a-zA-Z_][\w_]*)\s*:\s*(.+?)(?:\s*#.*)?$', line)
                            if match:
                                key, value = match.groups()
                                config_data[key.strip()] = value.strip().strip('"\'')
                    
                    elif file_type == 'env':
                        for line in content.split('\n'):
                            line = line.strip()
                            if line and not line.startswith('#'):
                                match = re.match(r'^([A-Z_][A-Z0-9_]*)\s*=\s*(.*)$', line)
                                if match:
                                    key, value = match.groups()
                                    config_data[key] = value.strip().strip('"\'')
                    
                    elif file_type == 'ini':
                        current_section = 'default'
                        for line in content.split('\n'):
                            line = line.strip()
                            if line.startswith('[') and line.endswith(']'):
                                current_section = line[1:-1]
                            elif '=' in line and not line.startswith('#'):
                                key, value = line.split('=', 1)
                                full_key = f"{current_section}.{key.strip()}" if current_section != 'default' else key.strip()
                                config_data[full_key] = value.strip().strip('"\'')
                    
                    elif file_type == 'py':
                        for line in content.split('\n'):
                            match = re.match(r'^([A-Z_][A-Z0-9_]*)\s*=\s*(.+?)(?:\s*#.*)?$', line)
                            if match:
                                key, value = match.groups()
                                config_data[key] = value.strip().strip('"\'')
                    
                    if config_data:
                        all_configs[config_file] = config_data
                
                except Exception as e:
                    logger.debug(f"Error parsing {config_file}: {e}")
        
        # Detect environment types
        env_mapping = {}
        for filename in all_configs.keys():
            if 'dev' in filename.lower() or 'local' in filename.lower():
                env_mapping[filename] = 'development'
            elif 'stag' in filename.lower():
                env_mapping[filename] = 'staging'
            elif 'prod' in filename.lower():
                env_mapping[filename] = 'production'
            elif 'test' in filename.lower():
                env_mapping[filename] = 'testing'
            else:
                env_mapping[filename] = 'unknown'
        
        # Collect all unique keys
        all_keys = set()
        for config_data in all_configs.values():
            all_keys.update(config_data.keys())
        
        # Find inconsistencies
        missing_vars = {}
        hardcoded_secrets = []
        security_risks = []
        variable_comparison = {}
        
        for key in all_keys:
            variable_comparison[key] = {}
            for filename, config_data in all_configs.items():
                if key in config_data:
                    value = config_data[key]
                    variable_comparison[key][filename] = value
                    
                    # Check for hardcoded secrets
                    if secret_patterns.search(key) and value and not value.startswith('$') and not value.upper().startswith('ENV:'):
                        if len(value) > 5 and not value.lower() in ['none', 'null', 'false', 'true']:
                            masked_value = value[:3] + '***' if len(value) > 6 else '***'
                            hardcoded_secrets.append({
                                'file': filename,
                                'key': key,
                                'value': masked_value,
                                'risk': 'HIGH' if 'prod' in filename.lower() else 'MEDIUM'
                            })
                    
                    # Check for security risks
                    if key.upper() == 'DEBUG' and value.lower() in ['true', '1', 'yes']:
                        env_type = env_mapping.get(filename, 'unknown')
                        if env_type in ['production', 'staging']:
                            security_risks.append({
                                'file': filename,
                                'issue': f'DEBUG=true in {env_type}',
                                'risk': 'HIGH' if env_type == 'production' else 'MEDIUM',
                                'recommendation': 'Set DEBUG=false in production/staging'
                            })
                else:
                    # Missing variable
                    env_type = env_mapping.get(filename, 'unknown')
                    if env_type not in missing_vars:
                        missing_vars[env_type] = []
                    if key not in missing_vars[env_type]:
                        missing_vars[env_type].append(key)
        
        # Scan code for environment variable usage
        env_var_usage = {}
        for ext in config["watched_extensions"]:
            for fp in project_root.rglob(f"*{ext}"):
                if fp.is_file() and not any(p.startswith('.') for p in fp.parts[:-1]):
                    try:
                        if fp.stat().st_size // 1024 > config["max_file_size_kb"]:
                            continue
                        
                        with open(fp, encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        for match in re.finditer(r'(?:os\.environ|process\.env|ENV)\[?["\']([A-Z_][A-Z0-9_]*)["\']?\]?', content):
                            var_name = match.group(1)
                            if var_name not in env_var_usage:
                                env_var_usage[var_name] = []
                            file_rel = str(fp.relative_to(project_root))
                            if file_rel not in env_var_usage[var_name]:
                                env_var_usage[var_name].append(file_rel)
                    
                    except Exception as e:
                        logger.debug(f"Error scanning {fp}: {e}")
        
        # Build result
        result = [""]
        result.append("=" * 70)
        result.append("🔧 CONFIGURATION ANALYSIS")
        result.append("=" * 70)
        result.append("")
        
        # Overview
        result.append("📁 **CONFIGURATION FILES**")
        total_files = sum(len(files) for files in config_files.values())
        result.append(f"  Total Files: {total_files}")
        for file_type, files in config_files.items():
            if files:
                result.append(f"  {file_type.upper()}: {len(files)} files")
                for f in files[:3]:
                    result.append(f"    • {f}")
                if len(files) > 3:
                    result.append(f"    ... and {len(files) - 3} more")
        result.append("")
        
        # Environment mapping
        result.append("🌍 **ENVIRONMENTS DETECTED**")
        env_counts = {}
        for env in env_mapping.values():
            env_counts[env] = env_counts.get(env, 0) + 1
        for env, count in sorted(env_counts.items()):
            result.append(f"  {env.title()}: {count} config files")
        result.append("")
        
        # Security Risks
        result.append("🚨 **SECURITY RISKS**")
        if security_risks:
            result.append(f"  Found: {len(security_risks)} issues")
            result.append("")
            for risk in security_risks:
                result.append(f"  ⚠️  {risk['file']}")
                result.append(f"    Issue: {risk['issue']}")
                result.append(f"    Risk: {risk['risk']}")
                result.append(f"    Action: {risk['recommendation']}")
                result.append("")
        else:
            result.append(f"  ✅ No security risks detected")
        result.append("")
        
        # Hardcoded Secrets
        result.append("🔐 **HARDCODED SECRETS**")
        if hardcoded_secrets:
            result.append(f"  Found: {len(hardcoded_secrets)} potential secrets")
            result.append("")
            for secret in hardcoded_secrets[:10]:
                result.append(f"  {secret['risk']} RISK: {secret['file']}")
                result.append(f"    Key: {secret['key']}")
                if include_examples:
                    result.append(f"    Value: {secret['value']}")
                result.append(f"    Action: Move to environment variable")
                result.append("")
            if len(hardcoded_secrets) > 10:
                result.append(f"  ... and {len(hardcoded_secrets) - 10} more")
            result.append("")
            result.append(f"  💡 Best Practice:")
            result.append(f"    • Store secrets in .env files (not in git)")
            result.append(f"    • Use environment variables")
            result.append(f"    • Add .env to .gitignore")
        else:
            result.append(f"  ✅ No hardcoded secrets detected")
        result.append("")
        
        # Missing Variables
        result.append("❓ **MISSING VARIABLES**")
        if missing_vars:
            for env, keys in sorted(missing_vars.items()):
                if keys:
                    result.append(f"  {env.title()}: {len(keys)} missing")
                    for key in keys[:5]:
                        result.append(f"    • {key}")
                    if len(keys) > 5:
                        result.append(f"    ... and {len(keys) - 5} more")
                    result.append("")
        else:
            result.append(f"  ✅ All variables present in all environments")
        result.append("")
        
        # Variable Comparison
        if include_examples and variable_comparison:
            result.append("📊 **VARIABLE COMPARISON** (Sample)")
            inconsistent = []
            for key, file_values in variable_comparison.items():
                if len(file_values) > 1:
                    values = set(file_values.values())
                    if len(values) > 1:
                        inconsistent.append((key, file_values))
            
            if inconsistent:
                result.append(f"  Inconsistent: {len(inconsistent)} variables")
                for key, file_values in inconsistent[:10]:
                    result.append(f"\n  {key}:")
                    for file, value in list(file_values.items())[:3]:
                        display_value = value if not secret_patterns.search(key) else value[:3] + '***'
                        result.append(f"    {file}: {display_value}")
                if len(inconsistent) > 10:
                    result.append(f"\n  ... and {len(inconsistent) - 10} more")
            else:
                result.append(f"  ✅ All shared variables have consistent values")
        result.append("")
        
        # Environment variable usage in code
        if env_var_usage:
            result.append("💻 **ENVIRONMENT VARIABLES USED IN CODE**")
            result.append(f"  Total: {len(env_var_usage)} variables")
            for var_name, files in sorted(env_var_usage.items())[:10]:
                result.append(f"\n  {var_name}:")
                for file in files[:3]:
                    result.append(f"    • {file}")
                if len(files) > 3:
                    result.append(f"    ... and {len(files) - 3} more files")
            if len(env_var_usage) > 10:
                result.append(f"\n  ... and {len(env_var_usage) - 10} more variables")
        result.append("")
        
        result.append("=" * 70)
        
        return "\n".join(result)
        
    except Exception as e:
        logger.error(f"Error in find_configuration_inconsistencies: {e}", exc_info=True)
        return f"❌ Error analyzing configuration: {str(e)}"
