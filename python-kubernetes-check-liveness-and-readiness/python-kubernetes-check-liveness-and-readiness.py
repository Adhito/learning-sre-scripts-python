#!/usr/bin/env python3
"""
Kubernetes Liveness & Readiness Probe Checker
Scans YAML files in a kustomize structure to verify probe configurations
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

class ProbeChecker:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.results = defaultdict(list)
        
    def find_yaml_files(self) -> List[Path]:
        """Recursively find all YAML files in the directory"""
        yaml_files = []
        for ext in ['*.yaml', '*.yml']:
            yaml_files.extend(self.base_path.rglob(ext))
        return sorted(yaml_files)
    
    def check_container_probes(self, container: dict, container_name: str) -> Dict[str, bool]:
        """Check if a container has liveness and readiness probes"""
        return {
            'livenessProbe': 'livenessProbe' in container,
            'readinessProbe': 'readinessProbe' in container,
            'container_name': container_name
        }
    
    def analyze_yaml_file(self, file_path: Path) -> List[Dict]:
        """Analyze a single YAML file for probe configurations"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Handle multi-document YAML files
                documents = yaml.safe_load_all(f)
                
                for doc_index, doc in enumerate(documents):
                    if not doc or not isinstance(doc, dict):
                        continue
                    
                    # Check if it's a Kubernetes resource with containers
                    kind = doc.get('kind', '')
                    metadata = doc.get('metadata', {})
                    resource_name = metadata.get('name', 'unnamed')
                    
                    # Look for containers in various resource types
                    containers = []
                    
                    if kind in ['Deployment', 'StatefulSet', 'DaemonSet', 'Job', 'CronJob']:
                        # Navigate to container specs
                        spec = doc.get('spec', {})
                        
                        if kind == 'CronJob':
                            template = spec.get('jobTemplate', {}).get('spec', {}).get('template', {})
                        elif kind == 'Job':
                            template = spec.get('template', {})
                        else:
                            template = spec.get('template', {})
                        
                        containers = template.get('spec', {}).get('containers', [])
                        init_containers = template.get('spec', {}).get('initContainers', [])
                        
                    elif kind == 'Pod':
                        containers = doc.get('spec', {}).get('containers', [])
                        init_containers = doc.get('spec', {}).get('initContainers', [])
                    
                    # Analyze regular containers
                    for container in containers:
                        container_name = container.get('name', 'unnamed')
                        probe_status = self.check_container_probes(container, container_name)
                        
                        findings.append({
                            'file': str(file_path.relative_to(self.base_path)),
                            'kind': kind,
                            'resource_name': resource_name,
                            'container_type': 'container',
                            'container_name': container_name,
                            'has_liveness': probe_status['livenessProbe'],
                            'has_readiness': probe_status['readinessProbe'],
                            'doc_index': doc_index
                        })
                    
                    # Analyze init containers (usually don't need probes, but good to track)
                    for container in init_containers:
                        container_name = container.get('name', 'unnamed')
                        probe_status = self.check_container_probes(container, container_name)
                        
                        findings.append({
                            'file': str(file_path.relative_to(self.base_path)),
                            'kind': kind,
                            'resource_name': resource_name,
                            'container_type': 'initContainer',
                            'container_name': container_name,
                            'has_liveness': probe_status['livenessProbe'],
                            'has_readiness': probe_status['readinessProbe'],
                            'doc_index': doc_index
                        })
                        
        except yaml.YAMLError as e:
            print(f"⚠️  YAML Error in {file_path.relative_to(self.base_path)}: {e}")
        except Exception as e:
            print(f"⚠️  Error processing {file_path.relative_to(self.base_path)}: {e}")
        
        return findings
    
    def scan_directory(self):
        """Scan all YAML files in the directory"""
        yaml_files = self.find_yaml_files()
        
        print(f"\n🔍 Scanning {len(yaml_files)} YAML files in {self.base_path}\n")
        print("=" * 80)
        
        all_findings = []
        
        for yaml_file in yaml_files:
            findings = self.analyze_yaml_file(yaml_file)
            all_findings.extend(findings)
        
        return all_findings
    
    def generate_report(self, findings: List[Dict]):
        """Generate a comprehensive report"""
        if not findings:
            print("\n✅ No containers found in YAML files (or no relevant Kubernetes resources)")
            return
        
        # Separate regular containers from init containers
        regular_containers = [f for f in findings if f['container_type'] == 'container']
        init_containers = [f for f in findings if f['container_type'] == 'initContainer']
        
        # Statistics for regular containers
        total_containers = len(regular_containers)
        with_both_probes = sum(1 for f in regular_containers if f['has_liveness'] and f['has_readiness'])
        with_liveness_only = sum(1 for f in regular_containers if f['has_liveness'] and not f['has_readiness'])
        with_readiness_only = sum(1 for f in regular_containers if not f['has_liveness'] and f['has_readiness'])
        without_probes = sum(1 for f in regular_containers if not f['has_liveness'] and not f['has_readiness'])
        
        print(f"\n📊 SUMMARY - Regular Containers")
        print("=" * 80)
        print(f"Total Containers: {total_containers}")
        print(f"✅ With Both Probes: {with_both_probes} ({with_both_probes/total_containers*100:.1f}%)")
        print(f"⚠️  With Liveness Only: {with_liveness_only} ({with_liveness_only/total_containers*100:.1f}%)")
        print(f"⚠️  With Readiness Only: {with_readiness_only} ({with_readiness_only/total_containers*100:.1f}%)")
        print(f"❌ Without Any Probes: {without_probes} ({without_probes/total_containers*100:.1f}%)")
        
        # Detailed findings for containers missing probes
        print(f"\n📋 DETAILED FINDINGS - Containers Missing Probes")
        print("=" * 80)
        
        missing_probes = [f for f in regular_containers if not (f['has_liveness'] and f['has_readiness'])]
        
        if not missing_probes:
            print("✅ All containers have both liveness and readiness probes!")
        else:
            for finding in missing_probes:
                status = []
                if not finding['has_liveness']:
                    status.append("❌ Missing livenessProbe")
                if not finding['has_readiness']:
                    status.append("❌ Missing readinessProbe")
                
                print(f"\n📄 File: {finding['file']}")
                print(f"   Kind: {finding['kind']}")
                print(f"   Resource: {finding['resource_name']}")
                print(f"   Container: {finding['container_name']}")
                print(f"   {' | '.join(status)}")
        
        # Init containers summary (if any)
        if init_containers:
            print(f"\n📊 INIT CONTAINERS ({len(init_containers)} found)")
            print("=" * 80)
            print("ℹ️  Init containers typically don't need probes, but listed for completeness:")
            for finding in init_containers:
                print(f"   • {finding['file']} - {finding['resource_name']}/{finding['container_name']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        print("=" * 80)
        if without_probes > 0:
            print("❗ Add both liveness and readiness probes to containers without them")
            print("   - livenessProbe: Detects if container needs to be restarted")
            print("   - readinessProbe: Detects if container is ready to serve traffic")
        if with_liveness_only > 0:
            print("⚠️  Add readiness probes to containers that only have liveness probes")
        if with_readiness_only > 0:
            print("⚠️  Add liveness probes to containers that only have readiness probes")
        if with_both_probes == total_containers:
            print("✅ Great! All containers have proper probe configurations!")


def main():
    """Main execution function"""
    import sys
    
    # Default path or accept from command line
    base_path = sys.argv[1] if len(sys.argv) > 1 else "kubernetes-kustomize-manifest/"
    
    if not os.path.exists(base_path):
        print(f"❌ Error: Directory '{base_path}' not found!")
        print(f"\nUsage: python {sys.argv[0]} [path_to_kustomize_directory]")
        sys.exit(1)
    
    checker = ProbeChecker(base_path)
    findings = checker.scan_directory()
    checker.generate_report(findings)
    
    print("\n" + "=" * 80)
    print("✅ Scan complete!\n")


if __name__ == "__main__":
    main()
