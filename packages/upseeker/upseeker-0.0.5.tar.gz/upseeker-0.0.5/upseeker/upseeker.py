import sys
import os
import platform
import importlib.util
import subprocess
import glob


def __bootstrap__():
   global __bootstrap__, __loader__, __file__
   import sys, pkg_resources, imp
   # Get the major and minor Python version
   py_version = f"{sys.version_info.major}{sys.version_info.minor}"
   # Get the operating system
   os_name = platform.system().lower()
   so_file = os.path.join(os.path.dirname(__file__),f"upseeker.cpython-{py_version}-{os_name}.so")
   spec = importlib.util.spec_from_file_location("upseeker", so_file)
   mylib = importlib.util.module_from_spec(spec)
   spec.loader.exec_module(mylib)


def set_new_SeekerPath(xrc, newdir):
   # The environment variable and value you want to set
   env_var = "SeekerPath"
   # The .xrc file
   xrc_file = os.path.expanduser(f"~/{xrc}")
   # Read the current .xrc file
   with open(xrc_file, "r") as file:
      lines = file.readlines()
   # Check if the environment variable is already set
   lines = [line for line in lines if not line.strip().startswith(f"export {env_var}=")]
   # Add the new environment variable setting
   lines.append(f"export {env_var}={newdir}\n")
   # Write the new .xrc file
   with open(xrc_file, "w") as file:
      file.writelines(lines)

   
def configure_distributed_run_directory():
   global __bootstrap__, __loader__, __file__
   import sys, pkg_resources, imp
   # Get the install path from the user
   path = os.path.expanduser(input("Please enter the absolute path to the new directory: "))
   with open(os.path.expanduser('~/.bashrc'), 'a') as bashrc:
      set_new_SeekerPath('.bashrc', path)
      print("\n\t\033[91mAttention: Please run 'source ~/.bashrc' in your shell!\033[0m")
   with open(os.path.expanduser('~/.zshrc'), 'a') as zshrc:
      set_new_SeekerPath('.zshrc', path)
      print("\n\t\033[91mAttention: Please run 'source ~/.zshrc' in your shell!\033[0m")
   sourcedir = os.path.dirname(os.path.realpath(__file__))
   source = os.path.join(sourcedir, f"scripts")
   target = os.path.join(path, f"scripts")
   subprocess.run(['cp', '-r', source, target], check=True)
   sh_files = glob.glob(f"{target}/*.sh")
   # Make each script executable
   for file in sh_files:
      subprocess.run(["chmod", "+x", file])    
   source = os.path.join(sourcedir, f"bin")
   target = os.path.join(path, f"bin")
   subprocess.run(['cp', '-r', source, target], check=True)
   subprocess.run(["chmod", "+x", f"{target}/coll"])
   print(f"\n\t\033[91mAttention: Please be sure to run this command: 'sudo spctl --add {target}/coll' \033[0m\n")
   target = os.path.join(path, f"tmp")
   subprocess.run(['mkdir', target], check=False, stderr=subprocess.DEVNULL)

   
__bootstrap__()

