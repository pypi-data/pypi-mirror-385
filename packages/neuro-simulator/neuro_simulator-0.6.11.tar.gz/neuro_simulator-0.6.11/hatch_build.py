
import os
import shutil
import subprocess
from sys import stderr

from hatchling.builders.hooks.plugin.interface import BuildHookInterface  # type: ignore


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        super().initialize(version, build_data)

        # # Check if build should be skipped
        # if os.environ.get('SKIP_BUILD', '').lower() in ('1', 'true', 'yes'):
        #     stderr.write(">>> Skipping frontend build (SKIP_BUILD=true)\n")
        #     return

        stderr.write(">>> Building dashboard frontend\n")
        
        dashboard_dir = os.path.join(self.root, 'dashboard')
        if not os.path.isdir(dashboard_dir):
            stderr.write(f">>> Frontend directory not found at {dashboard_dir}\n")
            return

        npm = shutil.which("npm")
        if npm is None:
            raise RuntimeError(
                "NodeJS `npm` is required for building the dashboard but it was not found"
            )
        
        stderr.write("### npm ci\n")
        subprocess.run([npm, "ci"], check=True, cwd=dashboard_dir)

        stderr.write("\n### npm run build\n")
        subprocess.run([npm, "run", "build"], check=True, cwd=dashboard_dir)

        stderr.write("\n>>> Building client frontend\n")
        
        client_dir = os.path.join(self.root, 'client')
        if not os.path.isdir(client_dir):
            stderr.write(f">>> Client directory not found at {client_dir}\n")
            # Note: This does not raise an error to allow building server-only in some scenarios
            return

        stderr.write("### npm ci\n")
        subprocess.run([npm, "ci"], check=True, cwd=client_dir)

        stderr.write("\n### npm run build\n")
        subprocess.run([npm, "run", "build"], check=True, cwd=client_dir)

