from repoman.package import read_package_list
from repoman import Workspace
import sys
import os
import tempfile

package_path = sys.argv[1]

package_specs = read_package_list(package_path)

# Prune subpackages for example
package_specs = [(package, spec) for (package, spec) in package_specs
                 if "/" not in package]

workspace_path = tempfile.mkdtemp()
print("Workspace: " + workspace_path)
workspace = Workspace(workspace_path)
workspace.checkout_packages(package_specs)
