"""
AI Project Cleaner & Analyzer
Senior-level automated project analysis and cleanup tool for AI agent projects

Author: Senior AI Engineer
Version: 1.0.0
"""

import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import json


@dataclass
class FileAnalysis:
    """Analysis results for a single file"""
    path: str
    category: str  # 'production', 'test', 'temp', 'docs', 'config'
    size_bytes: int
    imports: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    is_used: bool = True


@dataclass
class ProjectReport:
    """Complete project analysis report"""
    total_files: int = 0
    production_files: List[str] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    temp_files: List[str] = field(default_factory=list)
    unused_files: List[str] = field(default_factory=list)
    code_smells: Dict[str, List[str]] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class AIProjectAnalyzer:
    """Analyzes AI projects for cleanup and restructuring opportunities"""
    
    # File patterns for categorization
    TEST_PATTERNS = [
        r'test_.*\.py$',
        r'.*_test\.py$',
        r'.*_spec\.py$',
        r'.*\.test\.py$'
    ]
    
    TEMP_PATTERNS = [
        r'.*\.log$',
        r'.*\.txt$',  # Output logs
        r'.*\.tmp$',
        r'.*\.cache$',
        r'.*_output\..*$'
    ]
    
    CONFIG_PATTERNS = [
        r'\.env.*',
        r'.*\.yaml$',
        r'.*\.yml$',
        r'.*\.json$',
        r'.*\.toml$',
        r'requirements.*\.txt$',
        r'.*\.config\..*'
    ]
    
    DOCS_PATTERNS = [
        r'README.*\.md$',
        r'.*\.md$',
        r'.*\.rst$',
        r'CHANGELOG.*',
        r'LICENSE.*'
    ]
    
    # Directories to ignore
    IGNORE_DIRS = {
        '__pycache__', 'node_modules', '.git', '.venv', 'venv',
        'env', '.env', 'dist', 'build', '.next', 'out', '.kiro'
    }
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.files: Dict[str, FileAnalysis] = {}
        self.import_graph: Dict[str, Set[str]] = defaultdict(set)
        
    def analyze(self) -> ProjectReport:
        """Run complete project analysis"""
        print("🔍 Starting AI Project Analysis...")
        
        # Scan all files
        self._scan_files()
        
        # Analyze Python files
        self._analyze_python_files()
        
        # Build import graph
        self._build_import_graph()
        
        # Detect unused files
        self._detect_unused_files()
        
        # Find code smells
        code_smells = self._find_code_smells()
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        # Build report
        report = self._build_report(code_smells, recommendations)
        
        print("✅ Analysis complete!")
        return report
    
    def _scan_files(self):
        """Scan all files in project"""
        print("  📁 Scanning files...")
        
        for root, dirs, files in os.walk(self.project_root):
            # Remove ignored directories
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.project_root)
                
                category = self._categorize_file(str(rel_path))
                
                self.files[str(rel_path)] = FileAnalysis(
                    path=str(rel_path),
                    category=category,
                    size_bytes=file_path.stat().st_size
                )
    
    def _categorize_file(self, file_path: str) -> str:
        """Categorize file based on patterns"""
        filename = os.path.basename(file_path)
        
        # Check test patterns
        if any(re.match(pattern, filename) for pattern in self.TEST_PATTERNS):
            return 'test'
        
        # Check temp patterns
        if any(re.match(pattern, filename) for pattern in self.TEMP_PATTERNS):
            return 'temp'
        
        # Check config patterns
        if any(re.match(pattern, filename) for pattern in self.CONFIG_PATTERNS):
            return 'config'
        
        # Check docs patterns
        if any(re.match(pattern, filename) for pattern in self.DOCS_PATTERNS):
            return 'docs'
        
        return 'production'
    
    def _analyze_python_files(self):
        """Analyze Python files for imports, functions, classes"""
        print("  🐍 Analyzing Python files...")
        
        for rel_path, analysis in self.files.items():
            if not rel_path.endswith('.py'):
                continue
            
            file_path = self.project_root / rel_path
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                # Extract imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis.imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            analysis.imports.append(node.module)
                
                # Extract functions and classes
                for node in ast.iter_child_nodes(tree):
                    if isinstance(node, ast.FunctionDef):
                        analysis.functions.append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        analysis.classes.append(node.name)
                
            except Exception as e:
                analysis.issues.append(f"Parse error: {str(e)}")
    
    def _build_import_graph(self):
        """Build import dependency graph"""
        print("  🔗 Building import graph...")
        
        for rel_path, analysis in self.files.items():
            if not rel_path.endswith('.py'):
                continue
            
            module_name = rel_path.replace('/', '.').replace('\\', '.').replace('.py', '')
            
            for imp in analysis.imports:
                # Check if this is a local import
                if self._is_local_import(imp):
                    self.import_graph[module_name].add(imp)
    
    def _is_local_import(self, import_name: str) -> bool:
        """Check if import is from local project"""
        # Simple heuristic: check if any file matches
        for rel_path in self.files.keys():
            if rel_path.endswith('.py'):
                module = rel_path.replace('/', '.').replace('\\', '.').replace('.py', '')
                if import_name in module or module in import_name:
                    return True
        return False
    
    def _detect_unused_files(self):
        """Detect files that are never imported"""
        print("  🗑️  Detecting unused files...")
        
        # Get all imported modules
        imported_modules = set()
        for imports in self.import_graph.values():
            imported_modules.update(imports)
        
        # Check each Python file
        for rel_path, analysis in self.files.items():
            if not rel_path.endswith('.py'):
                continue
            
            if analysis.category in ['test', 'temp']:
                continue
            
            module_name = rel_path.replace('/', '.').replace('\\', '.').replace('.py', '')
            
            # Check if module is imported anywhere
            is_imported = any(module_name in imp or imp in module_name 
                            for imp in imported_modules)
            
            # Check if it's an entry point (has __main__)
            file_path = self.project_root / rel_path
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    is_entry_point = '__main__' in content
            except:
                is_entry_point = False
            
            if not is_imported and not is_entry_point:
                analysis.is_used = False
    
    def _find_code_smells(self) -> Dict[str, List[str]]:
        """Find code quality issues"""
        print("  👃 Detecting code smells...")
        
        smells = {
            'large_files': [],
            'no_docstrings': [],
            'many_imports': [],
            'god_classes': [],
            'duplicate_names': []
        }
        
        function_names = defaultdict(list)
        
        for rel_path, analysis in self.files.items():
            if not rel_path.endswith('.py'):
                continue
            
            # Large files (>500 lines)
            file_path = self.project_root / rel_path
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                    if lines > 500:
                        smells['large_files'].append(f"{rel_path} ({lines} lines)")
            except:
                pass
            
            # Many imports (>20)
            if len(analysis.imports) > 20:
                smells['many_imports'].append(f"{rel_path} ({len(analysis.imports)} imports)")
            
            # Track function names for duplicates
            for func in analysis.functions:
                function_names[func].append(rel_path)
        
        # Find duplicate function names
        for func_name, files in function_names.items():
            if len(files) > 1 and not func_name.startswith('_'):
                smells['duplicate_names'].append(f"{func_name} in {', '.join(files)}")
        
        return smells
    
    def _generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations"""
        print("  💡 Generating recommendations...")
        
        recommendations = []
        
        # Count files by category
        test_count = sum(1 for f in self.files.values() if f.category == 'test')
        temp_count = sum(1 for f in self.files.values() if f.category == 'temp')
        unused_count = sum(1 for f in self.files.values() if not f.is_used)
        
        if test_count > 0:
            recommendations.append(
                f"🧪 Move {test_count} test files to dedicated /tests directory"
            )
        
        if temp_count > 0:
            recommendations.append(
                f"🗑️  Remove {temp_count} temporary/log files"
            )
        
        if unused_count > 0:
            recommendations.append(
                f"⚠️  Review {unused_count} potentially unused files"
            )
        
        # Check for proper structure
        has_src = any('src/' in f.path or 'src\\' in f.path for f in self.files.values())
        if not has_src:
            recommendations.append(
                "📁 Consider organizing code in /src directory"
            )
        
        has_config = any(f.category == 'config' for f in self.files.values())
        if has_config:
            config_in_root = any(f.category == 'config' and '/' not in f.path and '\\' not in f.path 
                                for f in self.files.values())
            if config_in_root:
                recommendations.append(
                    "⚙️  Move configuration files to /config directory"
                )
        
        return recommendations
    
    def _build_report(self, code_smells: Dict, recommendations: List[str]) -> ProjectReport:
        """Build final report"""
        report = ProjectReport()
        
        report.total_files = len(self.files)
        
        for rel_path, analysis in self.files.items():
            if analysis.category == 'production':
                report.production_files.append(rel_path)
            elif analysis.category == 'test':
                report.test_files.append(rel_path)
            elif analysis.category == 'temp':
                report.temp_files.append(rel_path)
            
            if not analysis.is_used and analysis.category == 'production':
                report.unused_files.append(rel_path)
        
        report.code_smells = code_smells
        report.recommendations = recommendations
        
        return report
    
    def save_report(self, report: ProjectReport, output_path: str):
        """Save report to markdown file"""
        print(f"  💾 Saving report to {output_path}...")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 🧹 AI Project Cleanup Report\n\n")
            f.write(f"**Total Files Analyzed**: {report.total_files}\n\n")
            
            f.write("## 📊 File Classification\n\n")
            f.write(f"- **Production Files**: {len(report.production_files)}\n")
            f.write(f"- **Test Files**: {len(report.test_files)}\n")
            f.write(f"- **Temporary Files**: {len(report.temp_files)}\n")
            f.write(f"- **Unused Files**: {len(report.unused_files)}\n\n")
            
            if report.test_files:
                f.write("### 🧪 Test Files (should be in /tests)\n\n")
                for file in sorted(report.test_files):
                    f.write(f"- `{file}`\n")
                f.write("\n")
            
            if report.temp_files:
                f.write("### 🗑️ Temporary Files (safe to delete)\n\n")
                for file in sorted(report.temp_files):
                    f.write(f"- `{file}`\n")
                f.write("\n")
            
            if report.unused_files:
                f.write("### ⚠️ Potentially Unused Files\n\n")
                for file in sorted(report.unused_files):
                    f.write(f"- `{file}`\n")
                f.write("\n")
            
            if report.code_smells:
                f.write("## 👃 Code Smells Detected\n\n")
                for smell_type, items in report.code_smells.items():
                    if items:
                        f.write(f"### {smell_type.replace('_', ' ').title()}\n\n")
                        for item in items:
                            f.write(f"- {item}\n")
                        f.write("\n")
            
            if report.recommendations:
                f.write("## 💡 Recommendations\n\n")
                for rec in report.recommendations:
                    f.write(f"{rec}\n\n")
            
            f.write("---\n\n")
            f.write("*Generated by AI Project Cleaner v1.0.0*\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI Project Cleaner & Analyzer - Senior AI Engineering Tool"
    )
    parser.add_argument(
        '--project',
        default='.',
        help='Project root directory (default: current directory)'
    )
    parser.add_argument(
        '--output',
        default='PROJECT_ANALYSIS.md',
        help='Output report file (default: PROJECT_ANALYSIS.md)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🧹 AI Project Cleaner & Analyzer")
    print("   Senior-Level Engineering Tool")
    print("="*60 + "\n")
    
    analyzer = AIProjectAnalyzer(args.project)
    report = analyzer.analyze()
    analyzer.save_report(report, args.output)
    
    print("\n" + "="*60)
    print("✅ Analysis Complete!")
    print(f"📄 Report saved to: {args.output}")
    print("="*60 + "\n")
    
    # Print summary
    print("📋 Summary:")
    print(f"   Total Files: {report.total_files}")
    print(f"   Test Files: {len(report.test_files)}")
    print(f"   Temp Files: {len(report.temp_files)}")
    print(f"   Unused Files: {len(report.unused_files)}")
    print(f"   Recommendations: {len(report.recommendations)}\n")


if __name__ == '__main__':
    main()
