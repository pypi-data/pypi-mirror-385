import os
import errno
from sefrone_build.builder_utils import UtilsManager, EnvFileManager

DOCKER_COMPOSE = 'docker-compose' if os.name == 'nt' else 'docker compose'
COMPOSE_BUILD_FILES = '-f docker-compose.yml -f docker-compose.build.yml'
COMPOSE_FILE = '-f docker-compose.yml'

class DockerComposeManager:

    @staticmethod
    def prepare_compose_files(env_file: str, compose_template_folder_path: str):

        def process_compose(compose_file, env_vars, output_file_path):
            with open(compose_file, "r") as f:
                compose_str = f.read()
                
            for key, value in env_vars.items():
                compose_str = compose_str.replace(f"${key}", value)

            if not os.path.exists(os.path.dirname(output_file_path)):
                try:
                    os.makedirs(os.path.dirname(output_file_path))
                except OSError as exc: # Guard against race condition
                    if exc.errno!= errno.EEXIST:
                        raise

            with open(output_file_path, "w") as f:
                f.write(compose_str)

        env_vars = EnvFileManager.load_env_vars(env_file)

        process_compose(f"{compose_template_folder_path}/docker-compose.yml", env_vars, "./docker-compose.yml")
        process_compose(f"{compose_template_folder_path}/docker-compose.build.yml", env_vars, "./docker-compose.build.yml")

    @staticmethod
    def run_docker_service(service_name, args = None):
        print(f"Run {service_name} with args({args})...")
        if args:
            UtilsManager.run_command(f"{DOCKER_COMPOSE} {COMPOSE_FILE} run {args} {service_name}")
        else:
            UtilsManager.run_command(f"{DOCKER_COMPOSE} {COMPOSE_FILE} run {service_name}")
        print("Service run completed.")

    @staticmethod
    def build_docker_service(service_name, args = None):
        print(f"Build {service_name} with args({args})...")
        if args:
            UtilsManager.run_command(f"{DOCKER_COMPOSE} {COMPOSE_BUILD_FILES} build --build-arg {args} {service_name}")
        else:
            UtilsManager.run_command(f"{DOCKER_COMPOSE} {COMPOSE_BUILD_FILES} build {service_name}")
        print(f"{service_name} built successfully.")

    @staticmethod
    def start_docker_service(service_name):
        print(f"Starting {service_name} service")
        UtilsManager.run_command(f"{DOCKER_COMPOSE} {COMPOSE_FILE} up -d {service_name}")
        print(f"{service_name} service started successfully.")

    @staticmethod
    def docker_clean():
        print("Stopping and removing services...")
        UtilsManager.run_command(f"{DOCKER_COMPOSE} {COMPOSE_FILE} down")
