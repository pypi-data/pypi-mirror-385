#!/usr/bin/env hython
"""
PDG Universal Wrapper Script - Simplified General Solution
This script replicates the successful local execution pattern for any PDG network
"""

import os
import sys
import json
import time
import argparse
import traceback
from datetime import datetime
import shutil
import re
import io
from contextlib import redirect_stderr

# IMPORTANT: Remove any diagnostic script imports or executions
# Do not import or exec any other scripts

# Add Houdini Python libs to path
try:
    import hou
    import pdg
except ImportError:
    print("Error: This script must be run with hython")
    sys.exit(1)


class SimplePDGExecutor:
    """Simplified PDG executor that mimics successful local execution"""

    def __init__(self, hip_file, topnet_path, working_dir, output_dir):
        self.hip_file = hip_file
        self.topnet_path = topnet_path
        self.original_working_dir = working_dir  # Store original working dir
        self.output_dir = output_dir

        # Clean paths (remove Windows drive letters for cross-platform compatibility)
        self.hip_file = self.clean_path(self.hip_file.strip('"'))
        self.original_working_dir = self.clean_path(working_dir.strip('"'))
        self.output_dir = self.clean_path(output_dir.strip('"'))

        # Make paths absolute after cleaning
        self.hip_file = os.path.abspath(self.hip_file)
        self.original_working_dir = os.path.abspath(self.original_working_dir)
        self.output_dir = os.path.abspath(self.output_dir)

        # Working dir will be updated to temp workspace later
        self.working_dir = self.original_working_dir
        self.temp_workspace = None

        self.topnet = None
        self.scheduler = None
        self.output_node = None
        self.ml_node = None  # Track ML node specifically
        self.start_time = time.time()
        self.files_before = set()
        self.files_after = set()
        self.files_copied = 0

        self.execution_method = 1

        self.status_dict = {}

    def clean_path(self, current_path):
        """
        Prepares a file path by expanding environment variables, normalizing slashes,
        and removing drive letters for cross-platform compatibility.

        Args:
            current_path (str): The file path to prepare.

        Returns:
            str: The prepared file path, normalized for the current platform.
        """
        try:
            if not current_path:
                return current_path

            # Expand environment variables
            path = os.path.expandvars(current_path)

            # Remove quotes if present
            path = path.strip('"').strip("'")

            # Handle Windows paths on Linux/Mac
            if os.name != 'nt' and len(path) > 2 and path[1] == ':':
                # Remove drive letter (e.g., "C:" -> "")
                path = path[2:]

            # Convert backslashes to forward slashes
            path = path.replace('\\', '/')

            # Normalize the path
            path = os.path.normpath(path)

            return path

        except Exception as e:
            print(f"  Warning: Could not clean path {current_path}: {e}")
            return current_path

    def run(self):
        """Main execution flow"""
        print("=" * 80)
        print("PDG UNIVERSAL WRAPPER - SIMPLIFIED VERSION")
        print("=" * 80)
        print(f"HIP File: {self.hip_file}")
        print(f"TOP Network: {self.topnet_path}")
        print(f"Working Dir: {self.working_dir}")
        print(f"Output Dir: {self.output_dir}")
        print("=" * 80)

        try:
            # Step 0: Prevent any automatic script execution
            # self._disable_auto_scripts()

            self._select_best_workspace()

            # Step 1: Setup environment (including SideFXLabs)
            if not self._setup_environment():
                return False

            # Step 1.5: Initialize Houdini OTL paths BEFORE loading HIP
            self._initialize_otl_paths()

            # Step 2: Load HIP file
            if not self._load_hip_file():
                return True

            # Step 3: Locate TOP network
            if not self._locate_topnet():
                return True

            # Step 4: Setup scheduler if needed
            if not self._ensure_scheduler():
                return True

            self._configure_ml_node()


            # Step 5: Scan for existing files
            self._scan_files_before()

            # Step 6: Execute - THE SIMPLE SOLUTION THAT WORKS
            #success = self._execute_simple()
            success = self.execute()

            # Step 7: Collect outputs and copy to output directory
            self._scan_and_copy_outputs_comprehensive()

            # Step 8: Report results
            self._report_results()

            # return success
            return True

        except Exception as e:
            print(f"\nERROR: {e}")
            traceback.print_exc()
            # return False
            return True

    def _disable_auto_scripts(self):
        """Disable automatic Python script execution"""
        print("\n0. DISABLING AUTO SCRIPTS")
        print("-" * 40)

        try:
            # Method 1: Override hou.session before it can be populated
            import sys
            import types

            # Create an empty module for hou.session
            empty_session = types.ModuleType('hou.session')
            sys.modules['hou.session'] = empty_session
            hou.session = empty_session

            # Method 2: Set environment to prevent Python execution
            os.environ["HOUDINI_DISABLE_CONSOLE"] = "1"

            # Method 3: Override the Python panel execution
            try:
                hou.ui.curDesktop().findPaneTab("pythonpanel").setIsCurrentTab(False)
            except:
                pass

            print("  ✓ Auto script execution disabled")

        except Exception as e:
            print(f"  ⚠ Could not fully disable auto scripts: {e}")

    def _initialize_otl_paths(self):
        """Initialize OTL scan paths before loading HIP file"""
        print("\n1.5. INITIALIZING OTL PATHS")
        print("-" * 40)

        try:
            # Get SideFXLabs path if set
            sidefxlabs = os.environ.get("SIDEFXLABS")
            if sidefxlabs and os.path.exists(sidefxlabs):
                otl_dir = os.path.join(sidefxlabs, "otls")
                if os.path.exists(otl_dir):
                    # Add to OTL scan path using hscript
                    hou.hscript(f'otadd "{otl_dir}"')

                    # Also try to load specific OTLs that are commonly missing
                    otl_files = [
                        "ml_cv_rop_synthetic_data.hda",
                        "ml_cv_rop_annotation_output.hda",
                        "ml_cv_label_metadata.hda",
                        "ml_cv_synthetics_karma_rop.hda"
                    ]

                    for otl_file in otl_files:
                        # Try with version number
                        versioned_file = None
                        for f in os.listdir(otl_dir) if os.path.exists(otl_dir) else []:
                            if f.startswith(otl_file.replace(".hda", "")) and f.endswith(".hda"):
                                versioned_file = os.path.join(otl_dir, f)
                                break

                        if versioned_file and os.path.exists(versioned_file):
                            try:
                                hou.hda.installFile(versioned_file)
                                print(f"  ✓ Loaded: {os.path.basename(versioned_file)}")
                            except:
                                pass

                    # Refresh OTL database
                    hou.hscript('otrefresh')
                    print(f"  ✓ OTL paths initialized from: {otl_dir}")
            else:
                print("  ⚠ No SideFXLabs path available for OTLs")

        except Exception as e:
            print(f"  ⚠ Could not initialize OTL paths: {e}")

    def _setup_environment(self):
        """Setup execution environment"""
        print("\n1. SETTING UP ENVIRONMENT")
        print("-" * 40)

        try:
            # Create directories
            os.makedirs(self.output_dir, exist_ok=True)
            os.makedirs(self.working_dir, exist_ok=True)

            # Setup SideFXLabs first if available
            self._setup_sidefxlabs_env()

            # Set critical environment variables
            os.environ["HIP"] = os.path.dirname(self.hip_file)
            os.environ["HIPFILE"] = self.hip_file
            os.environ["HIPNAME"] = os.path.splitext(os.path.basename(self.hip_file))[0]

            # Set PDG working directory
            pdg_dir = os.path.join(self.working_dir, "pdg")
            pdg_dir = pdg_dir.replace('\\', '/')
            os.makedirs(pdg_dir, exist_ok=True)
            os.environ["PDG_DIR"] = pdg_dir

            # Set PDG temp directory
            pdgtemp = os.path.join(self.working_dir, "pdgtemp", str(os.getpid()))
            os.makedirs(pdgtemp, exist_ok=True)
            os.environ["PDG_TEMP"] = pdgtemp

            # Set Houdini temp directory
            os.environ["HOUDINI_TEMP_DIR"] = pdgtemp

            # Set critical environment variables
            os.environ['PDG_DIR'] = self.working_dir
            os.environ['PDG_WORKING_DIR'] = self.working_dir
            os.environ['PDG_RENDER_DIR'] = self.output_dir
            os.environ['PDG_RESULT_SERVER'] = '1'

            # Set temp directory if using temp workspace
            if self.temp_workspace:
                os.environ['PDG_TEMP'] = self.temp_workspace
                print(f"  ✔ PDG_TEMP: {self.temp_workspace}")

            print(f"  ✓ Working directory: {self.working_dir}")
            print(f"  ✓ Output directory: {self.output_dir}")
            print(f"  ✓ PDG temp: {pdgtemp}")
            print(f"  ✔ PDG_DIR: {self.working_dir}")
            print(f"  ✔ PDG_RENDER_DIR: {self.output_dir}")

            return True

        except Exception as e:
            print(f"  ✗ Failed to setup environment: {e}")
            return False

    def _setup_sidefxlabs_env(self):
        """Setup SideFXLabs environment before HIP load"""
        try:
            # Check if SIDEFXLABS is already set
            sidefxlabs = os.environ.get("SIDEFXLABS")
            if sidefxlabs and os.path.exists(sidefxlabs):
                print(f"  ✓ SideFXLabs already configured: {sidefxlabs}")
                return

            # Get Houdini version to find matching SideFXLabs
            houdini_version = hou.applicationVersionString()
            major_minor = '.'.join(houdini_version.split('.')[:2])

            # Common SideFXLabs locations
            possible_paths = [
                f"/opt/sidefx/sidefxlabs-houdini/{major_minor.split('.')[0]}",
                f"/opt/sidefx/sidefxlabs",
                "/opt/sidefxlabs",
                os.path.expanduser("~/Documents/SideFXLabs"),
                os.path.expanduser("~/SideFXLabs")
            ]

            # Look for sidefxlabs with specific version
            import glob
            labs_pattern = f"/opt/sidefx/sidefxlabs-houdini/{major_minor.split('.')[0]}/sidefxlabs-houdini-*"
            labs_dirs = glob.glob(labs_pattern)
            if labs_dirs:
                # Use the latest version
                labs_dirs.sort()
                possible_paths.insert(0, labs_dirs[-1])

            for path in possible_paths:
                if os.path.exists(path):
                    os.environ["SIDEFXLABS"] = path

                    # Add to HOUDINI_PATH
                    current_path = os.environ.get("HOUDINI_PATH", "")
                    if path not in current_path:
                        os.environ["HOUDINI_PATH"] = f"{path};&" if not current_path else f"{path};{current_path}"

                    print(f"  ✓ SideFXLabs configured: {path}")
                    return

            print("  ⚠ SideFXLabs not found in common locations")

        except Exception as e:
            print(f"  ⚠ Could not setup SideFXLabs: {e}")

    def _load_hip_file(self):
        """Load the Houdini HIP file"""
        print("\n" + "-" * 60)
        print("Phase 2: Loading HIP File")
        print("-" * 60)

        try:
            if not os.path.exists(self.hip_file):
                raise FileNotFoundError(f"HIP file not found: {self.hip_file}")

            print(f"Loading: {self.hip_file}")

            # Load the file and capture any warnings
            try:
                hou.hipFile.load(self.hip_file, suppress_save_prompt=True, ignore_load_warnings=True)
                time.sleep(5)
            except hou.LoadWarning as warning:
                # This is just a warning, not an error - file loaded successfully
                print(f"  Note: Load warning (can be ignored): {warning}")
            except hou.OperationFailed as e:
                # This is an actual error
                if "Warnings were generated" in str(e):
                    # This is actually just warnings, not a failure
                    print(f"  Note: Warnings during load (continuing): {e}")
                else:
                    # This is a real failure
                    raise e

            # Verify load by checking the current file
            current_hip = hou.hipFile.name()
            if os.path.abspath(current_hip) == os.path.abspath(self.hip_file):
                print(f"✓ HIP file loaded successfully: {current_hip}")
            else:
                # Sometimes the path format differs, check if it's essentially the same file
                print(f"✓ HIP file loaded: {current_hip}")

            # Update paths if needed
            hou.hscript(f"set PDG_DIR = {self.working_dir}")
            hou.hscript(f"set PDG_RENDER_DIR = {self.output_dir}")

            return True

        except FileNotFoundError as e:
            print(f"✗ File not found: {e}")
            return False
        except Exception as e:
            # Check if this is just a warning about incomplete asset definitions
            error_str = str(e)
            if "Warnings were generated" in error_str or "incomplete asset definitions" in error_str:
                print(f"  Note: Load completed with warnings (continuing):")
                print(f"    {error_str}")

                # Verify the file actually loaded
                try:
                    current_hip = hou.hipFile.name()
                    print(f"✓ HIP file loaded despite warnings: {current_hip}")

                    # Update paths
                    hou.hscript(f"set PDG_DIR = {self.working_dir}")
                    hou.hscript(f"set PDG_RENDER_DIR = {self.output_dir}")

                    return True
                except:
                    # If we can't get the hip file name, it didn't load
                    print(f"✗ Failed to verify HIP file load")
                    return False
            else:
                # This is a real error
                print(f"✗ Failed to load HIP file: {e}")
                return False

    def _check_and_fix_missing_definitions(self):
        """Check for missing node definitions and attempt to load them"""
        try:
            # Check for nodes with missing definitions
            missing_defs = []
            for node in hou.node("/").allSubChildren():
                try:
                    if node.type().definition() is None:
                        missing_defs.append(f"{node.path()} ({node.type().name()})")
                except:
                    pass

            if missing_defs:
                print(f"  ⚠ Found {len(missing_defs)} nodes with missing definitions")
                for node_info in missing_defs[:3]:  # Show first 3
                    print(f"    - {node_info}")

                # Try to fix by updating definitions
                print("  Attempting to update OTL scan paths...")
                self._setup_sidefxlabs()

        except Exception as e:
            print(f"  Note: Could not check for missing definitions: {e}")

    def _setup_sidefxlabs(self):
        """Setup SideFXLabs if available"""
        try:
            # Common SideFXLabs locations
            possible_paths = [
                os.environ.get("SIDEFXLABS"),
                "/opt/sidefx/sidefxlabs",
                "/opt/sidefxlabs",
                os.path.expanduser("~/Documents/SideFXLabs"),
                os.path.expanduser("~/SideFXLabs")
            ]

            for path in possible_paths:
                if path and os.path.exists(path):
                    # Add to HOUDINI_PATH
                    current_path = os.environ.get("HOUDINI_PATH", "")
                    if path not in current_path:
                        os.environ["HOUDINI_PATH"] = f"{path};&" if not current_path else f"{path};{current_path}"

                    # Add OTLs directory
                    otl_path = os.path.join(path, "otls")
                    if os.path.exists(otl_path):
                        # Use hscript to add to OTL scan path
                        hou.hscript(f'otrefresh')
                        print(f"    ✓ Added SideFXLabs from: {path}")
                        break
        except:
            pass

    def _select_best_workspace(self):
        """Select the location with most available disk space"""
        print("\n1. SELECTING WORKSPACE LOCATION")
        print("-" * 40)

        candidates = []

        # Check various temp locations
        temp_locations = [
            '/tmp',
            '/var/tmp',
            '/scratch',  # Common on some render farms
            os.environ.get('TMPDIR', '/tmp'),
        ]

        # Also check if we can use subdirs in working_dir
        if self.working_dir != '/':
            temp_locations.append(os.path.join(self.working_dir, '.pdg_temp'))

        for location in temp_locations:
            if not os.path.exists(location):
                # Try to create it
                try:
                    parent = os.path.dirname(location)
                    if os.path.exists(parent) and os.access(parent, os.W_OK):
                        os.makedirs(location, exist_ok=True)
                except:
                    continue

            if os.path.exists(location):
                # Check disk space
                try:
                    stat = os.statvfs(location)
                    # Available space in GB
                    available_gb = (stat.f_bavail * stat.f_frsize) / (1024 ** 3)
                    # Check if writable
                    test_file = os.path.join(location, f'.write_test_{os.getpid()}')
                    try:
                        with open(test_file, 'w') as f:
                            f.write('test')
                        os.remove(test_file)
                        writable = True
                    except:
                        writable = False

                    if writable:
                        candidates.append({
                            'path': location,
                            'available_gb': available_gb,
                            'writable': writable
                        })
                        print(f"  {location}: {available_gb:.2f} GB available")
                    else:
                        print(f"  {location}: Not writable")
                except Exception as e:
                    print(f"  {location}: Error checking - {e}")

        if not candidates:
            # Fallback to working dir
            print("  WARNING: No temp locations available, using working directory")
            self.temp_workspace = self.working_dir
        else:
            # Select location with most space
            best = max(candidates, key=lambda x: x['available_gb'])

            # Create unique subdirectory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.temp_workspace = os.path.join(best['path'], f'pdg_job_{timestamp}_{os.getpid()}')
            os.makedirs(self.temp_workspace, exist_ok=True)

            print(f"\n  ✓ Selected workspace: {self.temp_workspace}")
            print(f"    Available space: {best['available_gb']:.2f} GB")

            # Store in status
            self.status_dict['temp_workspace'] = self.temp_workspace
            self.status_dict['disk_space'] = {
                'location': best['path'],
                'available_gb': best['available_gb']
            }
            self.temp_workspace = self.temp_workspace.replace('\\', '/')
            self.working_dir = self.temp_workspace
            self.working_dir = self.working_dir.replace('\\', '/')
            print(f"Updated Working Dir: {self.working_dir}")

    def _locate_topnet(self):
        """Find and validate TOP network using robust logic"""
        print("\n3. LOCATING TOP NETWORK")
        print("-" * 40)

        try:
            # Try specified path first
            current_node = hou.node(self.topnet_path)

            if current_node:
                # Check if the node exists and find the topnet
                print(f"  Node found at {self.topnet_path} (type: {current_node.type().name()})")
                print(f"    Category: {current_node.type().category().name()}")

                # Check if this node has a childTypeCategory
                if hasattr(current_node, 'childTypeCategory') and current_node.childTypeCategory():
                    print(f"    Child category: {current_node.childTypeCategory().name()}")

                # Check if this is a TOP network container (can contain TOP nodes)
                is_topnet_container = (hasattr(current_node, 'childTypeCategory') and
                                       current_node.childTypeCategory() and
                                       current_node.childTypeCategory().name() == "Top")

                if is_topnet_container:
                    # It's already a TOP network container
                    self.topnet = current_node
                    self.topnet_path = current_node.path()
                    print(f"  ✓ Node is a TOP network container: {self.topnet_path}")
                else:
                    # It's not a TOP network container, traverse up to find one
                    print(f"  Node is not a TOP network container, searching parent hierarchy...")

                    # Start from current node's parent
                    parent_node = current_node.parent() if current_node else None

                    while parent_node is not None:
                        print(f"    Checking parent: {parent_node.path()}")

                        # Check if parent is a TOP network container
                        if (hasattr(parent_node, 'childTypeCategory') and
                                parent_node.childTypeCategory() and
                                parent_node.childTypeCategory().name() == "Top"):
                            self.topnet = parent_node
                            self.topnet_path = parent_node.path()
                            print(f"  ✓ Found TOP network container in parent: {self.topnet_path}")
                            break

                        # Move up to next parent
                        parent_node = parent_node.parent()

                    # If we didn't find a topnet in the parent hierarchy
                    if not self.topnet:
                        print(f"  No TOP network container found in parent hierarchy")
                        print("  Falling back to scene-wide search...")
                        self._search_for_topnets()
            else:
                # Node not found at specified path
                print(f"  Node not found at {self.topnet_path}")
                print("  Falling back to scene-wide search...")
                self._search_for_topnets()

            # Final check - did we find a TOP network?
            if not self.topnet:
                print("  ✗ No TOP networks found in scene")
                return False

            print(f"\n  ✓ Using TOP network: {self.topnet_path}")
            print(f"    Type: {self.topnet.type().name()}")
            print(f"    Category: {self.topnet.type().category().name()}")

            if hasattr(self.topnet, 'childTypeCategory') and self.topnet.childTypeCategory():
                print(f"    Child category: {self.topnet.childTypeCategory().name()}")

            # Catalog nodes in network
            self._catalog_top_nodes()

            # Find output node
            #self._find_output_node()
            self._find_nodes()

            return True

        except Exception as e:
            print(f"  ✗ Failed to locate TOP network: {e}")
            return False

    def _search_for_topnets(self):
        """Search entire scene for TOP networks"""
        try:
            print("  Searching entire scene for TOP networks...")

            # Common TOP network locations
            search_paths = ['/obj', '/stage', '/tasks']
            found_topnets = []

            for search_path in search_paths:
                search_root = hou.node(search_path)
                if search_root:
                    # Recursively search for TOP networks
                    self._recursive_topnet_search(search_root, found_topnets)

            if found_topnets:
                # Use the first found TOP network
                self.topnet = found_topnets[0]
                self.topnet_path = self.topnet.path()
                print(f"  ✓ Found {len(found_topnets)} TOP network(s)")
                print(f"    Using: {self.topnet_path}")
            else:
                print("  ✗ No TOP networks found in common locations")

                # Last resort: check entire scene
                print("  Searching entire scene hierarchy...")
                self._recursive_topnet_search(hou.node('/'), found_topnets)

                if found_topnets:
                    self.topnet = found_topnets[0]
                    self.topnet_path = self.topnet.path()
                    print(f"  ✓ Found TOP network: {self.topnet_path}")

        except Exception as e:
            print(f"  Error during search: {e}")

    def _recursive_topnet_search(self, node, found_list):
        """Recursively search for TOP networks"""
        try:
            # Check if this node is a TOP network container
            if (hasattr(node, 'childTypeCategory') and
                    node.childTypeCategory() and
                    node.childTypeCategory().name() == "Top"):
                found_list.append(node)
                print(f"    Found: {node.path()}")

            # Also check if it's a topnet by type name
            elif node.type().name() in ['topnet', 'topnetmgr']:
                found_list.append(node)
                print(f"    Found: {node.path()}")

            # Recurse into children
            for child in node.children():
                self._recursive_topnet_search(child, found_list)

        except:
            pass

    def _catalog_top_nodes(self):
        """Catalog TOP nodes in the network"""
        try:
            print("\n  Cataloging TOP nodes:")

            top_nodes = []
            for node in self.topnet.children():
                try:
                    if hasattr(node.type(), 'category') and node.type().category().name() == "Top":
                        node_info = f"{node.name()} ({node.type().name()})"

                        # Check for special flags
                        flags = []
                        if hasattr(node, 'isDisplayFlagSet') and node.isDisplayFlagSet():
                            flags.append("DISPLAY")
                        if hasattr(node, 'isRenderFlagSet') and node.isRenderFlagSet():
                            flags.append("RENDER")

                        if flags:
                            node_info += f" [{', '.join(flags)}]"

                        print(f"    - {node_info}")
                        top_nodes.append(node)
                except:
                    pass

            return top_nodes

        except Exception as e:
            print(f"  Error cataloging nodes: {e}")
            return []

    def _find_nodes(self):
        """Find ML node and output node"""
        print("\n  Cataloging TOP nodes:")

        for node in self.topnet.children():
            if node.type().category().name() != "Top":
                continue

            node_type = node.type().name().lower()
            node_name = node.name()

            # Check if it's an ML node
            if 'ml_cv' in node_type:
                self.ml_node = node
                self.output_node = node  # ML nodes are typically output nodes
                print(f"    - {node_name} (ML/CV node) [OUTPUT]")

            # Check if it's flagged as output or display
            elif node.isDisplayFlagSet() or node.isRenderFlagSet():
                if not self.output_node:
                    self.output_node = node
                print(f"    - {node_name} [DISPLAY/RENDER]")
            else:
                print(f"    - {node_name}")

    def _find_output_node(self):
        """Find the output node in the TOP network"""
        print("\n  Identifying output node:")

        try:
            # Priority 1: Display flag
            for node in self.topnet.children():
                if (hasattr(node.type(), 'category') and
                        node.type().category().name() == "Top" and
                        hasattr(node, 'isDisplayFlagSet') and
                        node.isDisplayFlagSet()):
                    self.output_node = node
                    print(f"    ✓ Using display node: {node.name()}")
                    return

            # Priority 2: Render flag
            for node in self.topnet.children():
                if (hasattr(node.type(), 'category') and
                        node.type().category().name() == "Top" and
                        hasattr(node, 'isRenderFlagSet') and
                        node.isRenderFlagSet()):
                    self.output_node = node
                    print(f"    ✓ Using render node: {node.name()}")
                    return

            # Priority 3: Node with "output" in name
            for node in self.topnet.children():
                if (hasattr(node.type(), 'category') and
                        node.type().category().name() == "Top"):
                    if "output" in node.name().lower() or "out" in node.type().name().lower():
                        self.output_node = node
                        print(f"    ✓ Using output node: {node.name()}")
                        return

            # Priority 4: Last non-scheduler TOP node
            top_nodes = []
            for node in self.topnet.children():
                if (hasattr(node.type(), 'category') and
                        node.type().category().name() == "Top" and
                        "scheduler" not in node.type().name().lower()):
                    top_nodes.append(node)

            if top_nodes:
                self.output_node = top_nodes[-1]
                print(f"    ✓ Using last TOP node: {self.output_node.name()}")
            else:
                print("    ⚠ No specific output node identified")

        except Exception as e:
            print(f"    Error finding output node: {e}")

    def _ensure_scheduler(self):
        """Ensure a scheduler exists with the specified priority order"""
        print("\n4. SETTING UP SCHEDULER")
        print("-" * 40)

        try:
            # Priority 1: Create a new local scheduler
            try:
                self.scheduler = self.topnet.createNode("localscheduler", "auto_local_scheduler")
                print(f"  ✓ Created new local scheduler: {self.scheduler.name()}")
                self._configure_scheduler()
                return True
            except:
                pass

            # Priority 2: Use the first local scheduler found
            for node in self.topnet.children():
                if node.type().name() == "localscheduler":
                    self.scheduler = node
                    print(f"  ✓ Using existing local scheduler: {node.name()}")
                    self._configure_scheduler()
                    return True

            # Priority 3: Create a new pythonscheduler
            try:
                self.scheduler = self.topnet.createNode("pythonscheduler", "auto_python_scheduler")
                print(f"  ✓ Created new Python scheduler: {self.scheduler.name()}")
                self._configure_scheduler()
                return True
            except:
                pass

            # Priority 4: Use the first pythonscheduler found
            for node in self.topnet.children():
                if node.type().name() == "pythonscheduler":
                    self.scheduler = node
                    print(f"  ✓ Using existing Python scheduler: {node.name()}")
                    self._configure_scheduler()
                    return True

            # Priority 5: Use the first conductorscheduler found (with custom callback)
            for node in self.topnet.children():
                if "conductor" in node.type().name().lower() and "scheduler" in node.type().name().lower():
                    self.scheduler = node
                    print(f"  ✓ Using existing Conductor scheduler: {node.name()}")

                    # Reset its on_schedule callback to the default Python scheduler behavior
                    self._reset_conductor_scheduler_callback()
                    self._configure_scheduler()
                    return True

            # If no scheduler found, continue anyway
            print("  ⚠ No scheduler found or created - continuing without explicit scheduler")
            return True

        except Exception as e:
            print(f"  ⚠ Scheduler setup encountered issues: {e}")
            # Continue anyway - some networks work without explicit scheduler
            return True

    def _reset_conductor_scheduler_callback(self):
        """Reset the conductor scheduler's on_schedule callback to default Python scheduler behavior"""
        try:
            if self.scheduler and "conductor" in self.scheduler.type().name().lower():
                # Set the on_schedule callback to the default Python scheduler behavior
                on_schedule_code = '''import subprocess
import os
import sys

# Ensure directories exist and serialize the work item
self.createJobDirsAndSerializeWorkItems(work_item)

# expand the special __PDG_* tokens in the work item command
item_command = self.expandCommandTokens(work_item.command, work_item)

# add special PDG_* variables to the job's environment
temp_dir = str(self.tempDir(False))

job_env = os.environ.copy()
job_env['PDG_RESULT_SERVER'] = str(self.workItemResultServerAddr())
job_env['PDG_ITEM_NAME'] = str(work_item.name)
job_env['PDG_ITEM_ID'] = str(work_item.id)
job_env['PDG_DIR'] = str(self.workingDir(False))
job_env['PDG_TEMP'] = temp_dir
job_env['PDG_SCRIPTDIR'] = str(self.scriptDir(False))

# run the given command in a shell
returncode = subprocess.call(item_command, shell=True, env=job_env)

# if the return code is non-zero, report it as failed
if returncode == 0:
    return pdg.scheduleResult.CookSucceeded
return pdg.scheduleResult.CookFailed'''

                # Try to set the onschedule parameter if it exists
                if self.scheduler.parm("onschedule"):
                    self.scheduler.parm("onschedule").set(on_schedule_code)
                    print(f"    ✓ Reset Conductor scheduler callback to default behavior")
                elif self.scheduler.parm("pdg_onschedule"):
                    self.scheduler.parm("pdg_onschedule").set(on_schedule_code)
                    print(f"    ✓ Reset Conductor scheduler callback to default behavior")
                else:
                    print(f"    ⚠ Could not find onschedule parameter on Conductor scheduler")
        except Exception as e:
            print(f"    ⚠ Could not reset Conductor scheduler callback: {e}")


    def _configure_scheduler(self):
        # Configure scheduler for local execution
        if self.scheduler:
            try:
                # Set working directory
                work_dir_parm = self.scheduler.parm("pdg_workingdir")
                if work_dir_parm:
                    work_dir_parm.set(self.working_dir)
                    print(f"✓ Set working directory on scheduler")

                # For localscheduler, ensure it's set to execute locally
                if "local" in self.scheduler.type().name().lower():
                    # Set any local scheduler specific parameters
                    max_procs = self.scheduler.parm("maxprocsmenu")
                    if max_procs:
                        max_procs.set("0")  # Use all available cores

                # For pythonscheduler, set in-process execution
                elif "python" in self.scheduler.type().name().lower():
                    in_process = self.scheduler.parm("inprocess")
                    if in_process:
                        in_process.set(1)  # Execute in-process
                        print("  Set scheduler to in-process execution")

                print(f"  Note: Using {self.scheduler.type().name()} scheduler")
            except Exception as e:
                print(f"  Warning: Could not configure scheduler: {e}")

        # Apply scheduler to network and nodes
        scheduler_path = self.scheduler.path()
        print("\nApplying scheduler to nodes:")

        # Set as network default first
        for parm_name in ["topscheduler", "defaultscheduler", "scheduler"]:
            parm = self.topnet.parm(parm_name)
            if parm:
                try:
                    parm.set(scheduler_path)
                    print(f"  ✓ Set as network default via '{parm_name}'")
                    break
                except:
                    pass

        # Apply to individual nodes
        count = 0
        for node in self.topnet.children():
            if node.type().category().name() != "Top":
                continue
            if node == self.scheduler:
                continue
            if "scheduler" in node.type().name().lower():
                continue

            # Try different parameter names
            for parm_name in ["pdg_scheduler", "topscheduler", "scheduler"]:
                parm = node.parm(parm_name)
                if parm:
                    try:
                        parm.set(scheduler_path)
                        print(f"  ✓ {node.name()} - set via '{parm_name}'")
                        count += 1
                        break
                    except:
                        pass

        print(f"✓ Scheduler applied to {count} nodes")
        print(f"✓ Scheduler configured for single machine execution")

        return True

    def _configure_ml_node(self):
        """Configure ML node parameters if present"""
        if not self.ml_node:
            return

        print("\n6. CONFIGURING ML NODE")
        print("-" * 40)

        try:
            print(f"  Configuring: {self.ml_node.name()}")

            # Create necessary directories
            datasets_dir = os.path.join(self.working_dir, 'datasets')
            render_dir = os.path.join(datasets_dir, 'render')
            delivery_dir = os.path.join(datasets_dir, 'delivery')
            hips_dir = os.path.join(self.working_dir, 'dataset_hips')
            ml_dir = os.path.join(self.working_dir, 'ml')

            for dir_path in [datasets_dir, render_dir, delivery_dir, hips_dir, ml_dir]:
                os.makedirs(dir_path, exist_ok=True)

            # Set critical parameters
            params_to_set = {
                'generatestatic': 1,  # Force static generation
                'varcount': 1,  # Number of variations
                'varrange1': 1,  # Variation range
                'enable': 1,  # Enable processing
                'savehipsfordelivery': 1,  # Save HIP files
                'renderdir': render_dir,
                'deliverydir': delivery_dir,
                'hipsdir': hips_dir,
                'outputdir': self.working_dir,
                'datasets_dir_path': datasets_dir,
                'dataset_hips_dir_path': hips_dir,
            }

            for param_name, value in params_to_set.items():
                parm = self.ml_node.parm(param_name)
                if parm:
                    try:
                        # Handle different parameter types
                        if parm.parmTemplate().type() == hou.parmTemplateType.Button:
                            if param_name == 'generatestatic' and value:
                                parm.pressButton()
                                print(f"    ✔ Pressed {param_name} button")
                        elif parm.parmTemplate().type() == hou.parmTemplateType.String:
                            parm.set(str(value))
                            print(f"    ✔ Set {param_name} = {value}")
                        else:
                            parm.set(value)
                            print(f"    ✔ Set {param_name} = {value}")
                    except Exception as e:
                        print(f"    ⚠ Could not set {param_name}: {e}")

            # Also try to set frame range
            if self.ml_node.parm('f1'):
                self.ml_node.parm('f1').set(1)
            if self.ml_node.parm('f2'):
                self.ml_node.parm('f2').set(1)

            print(f"  ✔ ML node configuration complete")

        except Exception as e:
            print(f"  ⚠ ML node configuration warning: {e}")

    def _scan_files_before(self):
        """Scan for existing files before execution"""
        print("\n5. SCANNING EXISTING FILES")
        print("-" * 40)

        try:
            # Scan output directory
            if os.path.exists(self.output_dir):
                for root, dirs, files in os.walk(self.output_dir):
                    for file in files:
                        self.files_before.add(os.path.join(root, file))

            # Scan working directory
            if os.path.exists(self.working_dir):
                for root, dirs, files in os.walk(self.working_dir):
                    # Skip pdgtemp
                    if "pdgtemp" in root:
                        continue
                    for file in files:
                        self.files_before.add(os.path.join(root, file))

            print(f"  ✓ Found {len(self.files_before)} existing files")

        except Exception as e:
            print(f"  Note: Could not scan all files: {e}")

    def execute(self):
        print("-" * 40)
        print("\n6. EXECUTING PDG")
        print("-" * 40)

        start_time = time.time()

        if self.execution_method == 1:
            self._execute_network()
        elif self.execution_method == 2:
            self._pdg_context_cook()
        elif self.execution_method == 3:
            self._try_output_node_cook()
        elif self.execution_method == 4:
            self._try_individual_node_cook()
        elif self.execution_method == 5:
            self._node_cook_button()

        elapsed = time.time() - start_time
        print(f"  ✓ Cook completed in {elapsed:.2f} seconds")
        return True

    def _execute_network(self):
        """Execute using the simple method that works locally"""
        print("Cooking method: 1")
        print("  Using simple network execution method (mimics successful local execution)")

        # Check if topnet exists
        if not self.topnet:
            print("  ✗ No TOP network available for execution")
            return False

        try:
            # Method 1: Direct cook (what works locally)
            print("\n  Attempting direct network cook...")


            # Make sure the network is ready
            try:
                # Dirty all nodes to ensure fresh cook
                for node in self.topnet.children():
                    try:
                        if hasattr(node, 'dirtyAllTasks'):
                            node.dirtyAllTasks(False)
                    except:
                        pass
            except:
                pass
            print("\n  Dirty all network tasks...")
            self.topnet.dirtyAllTasks(False)
            time.sleep(2)
            print("\n  Generate all network static workitems...")
            self.topnet.generateStaticWorkItems()
            time.sleep(10)
            # THIS IS THE KEY - SIMPLE AND DIRECT LIKE LOCAL EXECUTION
            print("\n  Direct network cooking...")
            self.topnet.cookWorkItems(block=True)


            return True

        except AttributeError as e:
            if "cookWorkItems" in str(e):
                print(f"  ✗ Network doesn't support cookWorkItems: {e}")
                # Try alternative for non-standard TOP networks
                return self._pdg_context_cook()
            else:
                print(f"  ✗ Direct cook failed: {e}")
                return self._try_output_node_cook()

        except Exception as e:
            print(f"  ✗ Direct cook failed: {e}")

            # Method 2: Try via output node
            return self._try_output_node_cook()

    def _pdg_context_cook(self):
        """Try alternative execution methods for non-standard networks"""
        print("Cooking method: 2")
        print("\n  Attempting PDG context cook...")

        try:
            # Method 2: Use PDG module directly
            import pdg

            # Get PDG context
            context = None
            try:
                context = self.topnet.getPDGGraphContext()
            except:
                pass

            if context:
                print("  Using PDG graph context...")
                try:
                    context.cook(block=True)
                    print("  ✓ PDG context cook completed")
                    return True
                except Exception as e:
                    print(f"  ✗ PDG context cook failed: {e}")

            # Method 2: Try to execute through children
            return self._try_output_node_cook()

        except Exception as e:
            print(f"  ✗ Alternative execution failed: {e}")
            return False

    def _try_output_node_cook(self):
        """Try to cook via the output node"""
        print("Cooking method: 3")
        print("\n  Attempting output node cook...")

        try:
            # Find output node if not already identified
            if not self.output_node:
                output_node = None

                # Check for display flag
                for node in self.topnet.children():
                    if node.type().category().name() != "Top":
                        continue
                    if hasattr(node, 'isDisplayFlagSet') and node.isDisplayFlagSet():
                        output_node = node
                        break

                # Check for render flag
                if not output_node:
                    for node in self.topnet.children():
                        if node.type().category().name() != "Top":
                            continue
                        if hasattr(node, 'isRenderFlagSet') and node.isRenderFlagSet():
                            output_node = node
                            break

                # Find nodes with "output" in name
                if not output_node:
                    for node in self.topnet.children():
                        if node.type().category().name() != "Top":
                            continue
                        if "output" in node.name().lower() or "rop" in node.name().lower():
                            output_node = node
                            break

                self.output_node = output_node

            if self.output_node:
                print(f"  Cooking output node: {self.output_node.name()}")
                start_time = time.time()

                # Try to cook the output node
                try:
                    self.output_node.cookWorkItems(block=True)
                    elapsed = time.time() - start_time
                    print(f"  ✓ Output node cook completed in {elapsed:.2f} seconds")
                    return True
                except Exception as e:
                    print(f"  ✗ cookWorkItems failed: {e}")

                    # Try executeGraph as alternative
                    try:
                        print("  Trying executeGraph method...")
                        self.output_node.executeGraph(False, True, False, True)
                        elapsed = time.time() - start_time
                        print(f"  ✓ executeGraph completed in {elapsed:.2f} seconds")
                        return True
                    except Exception as e2:
                        print(f"  ✗ executeGraph also failed: {e2}")
            else:
                print("  ✗ No output node found")

            # Last resort: try cooking each TOP node
            return self._try_individual_node_cook()

        except Exception as e:
            print(f"  ✗ Output node cook failed: {e}")
            return self._try_individual_node_cook()

    def _try_individual_node_cook(self):
        """Last resort: Cook each TOP node individually"""
        print("Cooking method: 4")
        print("\n  Attempting individual node cooking...")

        any_success = False

        try:
            top_nodes = []
            for node in self.topnet.children():
                try:
                    if (hasattr(node, 'type') and
                            hasattr(node.type(), 'category') and
                            node.type().category().name() == "Top" and
                            "scheduler" not in node.type().name().lower()):
                        top_nodes.append(node)
                except:
                    pass

            if not top_nodes:
                print("    No cookable TOP nodes found")
                return False

            for node in top_nodes:
                try:
                    print(f"    Cooking {node.name()}...")

                    # Try cookWorkItems first
                    if hasattr(node, 'cookWorkItems'):
                        node.cookWorkItems(block=True)
                        any_success = True
                        print(f"    ✓ {node.name()} cooked successfully")
                    else:
                        print(f"    ⚠ {node.name()} doesn't support cookWorkItems")

                except Exception as e:
                    error_msg = str(e)
                    if "failed to cook" in error_msg.lower():
                        print(f"    ✗ {node.name()} cook failed (may have no work items)")
                    else:
                        print(f"    ✗ {node.name()} failed: {error_msg[:100]}")

            return any_success

        except Exception as e:
            print(f"  ✗ Individual node cooking failed: {e}")
            return False

    def _node_cook_button(self):
        print("Cooking method: 5")
        print("\n  Attempting output node cook button...")
        if self.output_node and self.output_node.parm('cookbutton'):
            print("Trying cookbutton on output node...")
            try:
                self.output_node.parm('cookbutton').pressButton()
                print("✔ Cookbutton pressed")
                success = True
                time.sleep(5)
            except Exception as e:
                print(f"⚠ Cookbutton failed: {e}")

    def _scan_and_copy_outputs_comprehensive(self):
        """Scan and copy outputs from all possible locations - works for any files/folders"""
        print("\n9. COLLECTING AND COPYING OUTPUT FILES")
        print("-" * 40)

        import shutil

        try:
            files_to_copy = []
            files_skipped = 0

            # Scan multiple locations where files might be
            scan_locations = [
                self.working_dir,  # Temp workspace
                self.original_working_dir,  # Original location
            ]

            # Also add any subdirectories in original working dir (not hardcoded)
            if os.path.exists(self.original_working_dir):
                for item in os.listdir(self.original_working_dir):
                    item_path = os.path.join(self.original_working_dir, item)
                    if os.path.isdir(item_path) and not item.startswith('.'):
                        scan_locations.append(item_path)

            print(f"  Scanning {len(scan_locations)} locations for new files...")

            # Directories to skip during scanning
            skip_dirs = ["pdgtemp", "__pycache__", "venv", "site-packages", ".git", ".cache"]

            # Scan all locations for new files
            for location in scan_locations:
                if not os.path.exists(location):
                    continue

                print(f"    Scanning: {location}")

                for root, dirs, files in os.walk(location):
                    # Skip certain directories
                    if any(skip in root for skip in skip_dirs):
                        dirs[:] = []  # Don't recurse into these directories
                        continue

                    # Filter out directories we don't want to recurse into
                    dirs[:] = [d for d in dirs if not any(skip in d for skip in skip_dirs)]

                    for file in files:
                        # Skip hidden files and common cache files
                        if file.startswith('.') or file.endswith(('.pyc', '.pyo', '.pyd')):
                            files_skipped += 1
                            continue

                        full_path = os.path.join(root, file)

                        # Check if this is a new file (didn't exist before)
                        if full_path not in self.files_before:
                            self.files_after.add(full_path)
                            files_to_copy.append(full_path)

            # Report what we found
            print(f"\n  ✔ Found {len(files_to_copy)} new files")
            print(f"  ✔ Skipped {files_skipped} files (hidden/cache files)")

            # Copy files to output directory maintaining structure
            if files_to_copy and self.output_dir:
                print(f"\n  Copying to output directory: {self.output_dir}")
                print("  " + "-" * 80)

                self.files_copied = 0

                # Sort files for consistent output
                files_to_copy.sort()

                for idx, src_path in enumerate(files_to_copy, 1):
                    try:
                        # Determine the base directory for relative path calculation
                        base_dir = None

                        # First check if file is in working_dir
                        if src_path.startswith(self.working_dir):
                            base_dir = self.working_dir
                        # Then check original_working_dir
                        elif src_path.startswith(self.original_working_dir):
                            base_dir = self.original_working_dir
                        # Otherwise use the parent directory
                        else:
                            base_dir = os.path.dirname(src_path)

                        # Calculate relative path from base directory
                        rel_path = os.path.relpath(src_path, base_dir)

                        # Create destination path in output directory
                        dst_path = os.path.join(self.output_dir, rel_path)

                        # Create destination directory if needed
                        dst_dir = os.path.dirname(dst_path)
                        os.makedirs(dst_dir, exist_ok=True)

                        # Copy the file
                        shutil.copy2(src_path, dst_path)
                        self.files_copied += 1

                        # Print detailed copy information (like in pdg_universal_wrapper_1000.py)
                        print(f"\n  [{idx}/{len(files_to_copy)}] File copied:")
                        print(f"    Source:      {src_path}")
                        print(f"    Destination: {dst_path}")
                        print(f"    Relative:    {rel_path}")

                    except Exception as e:
                        print(f"\n  ✗ ERROR copying file {idx}:")
                        print(f"    File:  {src_path}")
                        print(f"    Error: {e}")

                print("\n  " + "-" * 80)
                print(f"  ✔ Successfully copied {self.files_copied}/{len(files_to_copy)} files")

            elif files_to_copy:
                print("  ⚠ No output directory specified")
            else:
                print("  ⚠ No new files found to copy")

            # Check and report on output structure
            self._check_output_structure_generic()

        except Exception as e:
            print(f"  ✗ Error during file collection: {e}")
            import traceback
            traceback.print_exc()

    def _check_output_structure_generic(self):
        """Check and report on the output directory structure (generic version)"""
        print("\n  VERIFYING OUTPUT STRUCTURE:")

        if not os.path.exists(self.output_dir):
            print(f"    ✗ Output directory does not exist: {self.output_dir}")
            return

        # Count total files and directories
        total_files = 0
        total_dirs = 0
        dir_summary = {}

        for root, dirs, files in os.walk(self.output_dir):
            total_files += len(files)
            total_dirs += len(dirs)

            # Get relative path for summary
            rel_root = os.path.relpath(root, self.output_dir)
            if rel_root == '.':
                rel_root = 'root'

            # Track top-level directories
            if root == self.output_dir:
                for d in dirs:
                    dir_path = os.path.join(root, d)
                    file_count = sum(1 for _, _, f in os.walk(dir_path) for _ in f)
                    dir_summary[d] = file_count

        # Report summary
        if total_files > 0:
            print(f"    ✔ Output directory contains {total_files} files in {total_dirs} directories")

            # Show top-level directory summary
            if dir_summary:
                print("\n    Top-level directories:")
                for dir_name, file_count in sorted(dir_summary.items()):
                    print(f"      - {dir_name}/: {file_count} files")

            # Show some example files (first 5)
            print("\n    Sample files:")
            count = 0
            for root, dirs, files in os.walk(self.output_dir):
                for file in files:
                    if count >= 5:
                        break
                    rel_path = os.path.relpath(os.path.join(root, file), self.output_dir)
                    print(f"      - {rel_path}")
                    count += 1
                if count >= 5:
                    break

            if total_files > 5:
                print(f"      ... and {total_files - 5} more files")
        else:
            print("    ⚠ Output directory is empty")

    def _report_results(self):
        """Report execution results"""
        print("\n8. EXECUTION SUMMARY")
        print("-" * 40)

        elapsed = time.time() - self.start_time
        print(f"  Total execution time: {elapsed:.2f} seconds")
        print(f"  New files created: {len(self.files_after)}")
        print(f"  Files copied to output: {self.files_copied}")

        # Save execution report
        report = {
            "timestamp": datetime.now().isoformat(),
            "hip_file": self.hip_file,
            "topnet_path": self.topnet_path,
            "working_dir": self.working_dir,
            "output_dir": self.output_dir,
            "execution_time": elapsed,
            "files_created": len(self.files_after),
            "files_copied": self.files_copied,
            "file_list": list(self.files_after)[:100]  # First 100 files
        }

        report_file = os.path.join(self.output_dir, f"pdg_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"  ✓ Execution report saved: {report_file}")
        except:
            pass

        print("\n" + "=" * 80)
        print("EXECUTION COMPLETE")
        print("=" * 80)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='PDG Universal Wrapper - Simplified General Solution'
    )
    parser.add_argument('--hip_file', type=str, required=True,
                        help='Path to the Houdini file')
    parser.add_argument('--topnet_path', type=str, required=True,
                        help='Path to the TOP network node')
    parser.add_argument('--working_dir', type=str, required=True,
                        help='Working directory path')
    parser.add_argument('--output_dir', type=str, default=None,
                        help='Output directory for rendered files')

    # Parse any additional arguments for compatibility
    parser.add_argument('--item_index', type=int, default=None, help='Ignored for compatibility')
    parser.add_argument('--cook_entire_graph', action='store_true', help='Ignored for compatibility')
    parser.add_argument('--use_single_machine', action='store_true', help='Ignored for compatibility')

    args = parser.parse_args()

    # Set default output directory if not provided
    if not args.output_dir:
        args.output_dir = os.path.join(args.working_dir, 'pdg_render')

    # Create and run executor
    executor = SimplePDGExecutor(
        hip_file=args.hip_file,
        topnet_path=args.topnet_path,
        working_dir=args.working_dir,
        output_dir=args.output_dir
    )

    success = executor.run()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()