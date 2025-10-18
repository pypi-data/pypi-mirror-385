import errno
import os
import subprocess

class EnvFileManager:
    @staticmethod
    def read_env_value(env_file_path, env_var):
        with open(env_file_path, 'r') as file:
            for line in file:
                if line.startswith(f'{env_var}='):
                    return line[len(f'{env_var}='):].strip()
            else:
                return None

    @staticmethod
    def load_env_vars(env_file_path):
        env_vars: dict[str, str] = {}
        with open(env_file_path, 'r') as file:
            for line in file:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
        return env_vars

    @staticmethod
    def save_env_vars(env_vars, env_file_path):
        with open(env_file_path, 'w') as file:
            for key, value in env_vars.items():
                file.write(f"{key}={value}\n")
    
    @staticmethod
    def is_linux_os():
        return os.name == 'posix' and 'linux' in os.sys.platform.lower()
    
    @staticmethod
    def is_windows_os():
        return os.name == 'nt'

class UtilsManager:
    @staticmethod
    def run_command(command):
        print(f"Executing: {command}")
        subprocess.run(command, shell=True, check=True)

    @staticmethod
    def open_browser(url: str):
        print("Opening browser...")
        os.system(f'start {url}')

    @staticmethod
    def move_file(source, destination):
        if not os.path.exists(os.path.dirname(destination)):
            try:
                os.makedirs(os.path.dirname(destination))
            except OSError as exc: # Guard against race condition
                if exc.errno!= errno.EEXIST:
                    raise
        
        with open(source, "r") as f:
            source_str = f.read()
        with open(destination, "w") as f:
            f.write(source_str)

    @staticmethod
    def set_current_directory(path: str):
        os.chdir(path)
        current_directory = os.getcwd()
        print("Current Directory:", current_directory)