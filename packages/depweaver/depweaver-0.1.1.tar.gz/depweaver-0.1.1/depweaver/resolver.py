# pyresolve/resolver.py

import requests
import sys
import os
import time
import json
from packaging.specifiers import SpecifierSet
from packaging.version import Version, InvalidVersion
from packaging.markers import Marker
from packaging.requirements import Requirement

class Resolver:
    def __init__(self):
        self.resolved_versions = {}
        self.constraints = {}
        self._info_cache = {}
        
        # --- START OF CACHING SETUP ---
        # Define the cache directory in the user's home folder
        self.cache_dir = os.path.join(os.path.expanduser("~"), ".pyresolve_cache")
        # Set the cache to be valid for 1 day (86400 seconds)
        self.cache_ttl = 86400 
        # Ensure the cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        # --- END OF CACHING SETUP ---

        self.current_python_version = Version(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        self.environment = {
            'python_version': f'{sys.version_info.major}.{sys.version_info.minor}',
            'sys_platform': sys.platform,
        }

    def get_package_info(self, package_name: str) -> dict | None:
        """
        Fetches package metadata, using a local file cache to avoid re-fetching.
        """
        # --- START OF CACHING LOGIC ---
        cache_file_path = os.path.join(self.cache_dir, f"{package_name}.json")

        # 1. Check if a fresh cache file exists
        if os.path.exists(cache_file_path):
            file_age = time.time() - os.path.getmtime(cache_file_path)
            if file_age < self.cache_ttl:
                print(f"✅ Using cached data for '{package_name}'...")
                with open(cache_file_path, "r") as f:
                    return json.load(f)
        # --- END OF CACHING LOGIC ---
        
        url = f"https://pypi.org/pypi/{package_name}/json"
        print(f"🔎 Fetching fresh metadata for '{package_name}'...")
        try:
            response = requests.get(url)
            response.raise_for_status()
            info = response.json()
            
            # --- START OF CACHING LOGIC ---
            # 2. Save the newly fetched data to the cache
            with open(cache_file_path, "w") as f:
                json.dump(info, f)
            # --- END OF CACHING LOGIC ---
            
            return info
        except (requests.exceptions.HTTPError, requests.exceptions.RequestException):
            print(f"❌ Could not find or fetch package '{package_name}' on PyPI.")
            return None

    # The rest of the file remains the same...
    def solve(self, packages: list[str]) -> list[str] | None:
        print("--- Building Dependency Graph and Collecting Constraints ---")
        self._collect_constraints_for_all(packages)

        print("\n--- Solving Version Constraints ---")
        all_packages_sorted = sorted(list(self.constraints.keys()))
        
        if self._backtrack_solve(all_packages_sorted):
            print("\n✅ Successfully resolved all dependencies.")
            return sorted([f"{name}=={version}" for name, version in self.resolved_versions.items()])
        else:
            print("\n❌ Failed to resolve dependencies.")
            return None

    def _collect_constraints_for_all(self, packages: list[str]):
        to_process = list(packages)
        processed = set()

        while to_process:
            requirement_string = to_process.pop(0)
            try:
                req = Requirement(requirement_string)
            except Exception:
                print(f"⚠️  Skipping invalid requirement string: {requirement_string}")
                continue

            if req.marker and not req.marker.evaluate(environment=self.environment):
                continue
            
            self.constraints.setdefault(req.name, []).append(req.specifier)

            if req.name in processed:
                continue
            
            processed.add(req.name)

            info = self.get_package_info(req.name)
            if not info: continue

            dependencies = info["info"].get("requires_dist") or []
            for dep in dependencies:
                if "extra ==" not in dep:
                    to_process.append(dep)

    def _backtrack_solve(self, packages_to_solve: list[str]) -> bool:
        if not packages_to_solve:
            return True

        pkg_name = packages_to_solve[0]
        remaining_packages = packages_to_solve[1:]
        
        print(f"🧠 Trying to solve for {pkg_name}...")

        all_specs = SpecifierSet()
        for spec in self.constraints.get(pkg_name, []):
            all_specs &= spec
        
        info = self.get_package_info(pkg_name)
        if not info: return False

        valid_versions = []
        for v_str in info["releases"].keys():
            try:
                Version(v_str)
                valid_versions.append(v_str)
            except InvalidVersion:
                print(f"⚠️  Ignoring invalid version format for {pkg_name}: {v_str}")
        
        for version_str in sorted(valid_versions, key=Version, reverse=True):
            version = Version(version_str)
            
            if version.is_prerelease or not all_specs.contains(version):
                continue

            self.resolved_versions[pkg_name] = version
            
            if self._backtrack_solve(remaining_packages):
                return True

        if pkg_name in self.resolved_versions:
            del self.resolved_versions[pkg_name]
            
        print(f"⏪ Backtracking from {pkg_name}...")
        return False

def solve_dependencies(packages: list[str]) -> list[str] | None:
    resolver = Resolver()
    return resolver.solve(packages)