import os
import requests

from sefrone_build.builder_utils import EnvFileManager

class BitbucketEnvManager:
    def __init__(self):
        self.token = self._get_required_os_env_var("BITBUCKET_REPO_ENV_ACCESS_TOKEN")
        self.workspace = self._get_required_os_env_var("BITBUCKET_WORKSPACE")
        self.repo_slug = self._get_required_os_env_var("BITBUCKET_REPO_SLUG")
        self.target_env = self._get_required_os_env_var("BITBUCKET_TARGET_ENV")

    def _get_required_os_env_var(self, name):
        value = os.getenv(name)
        if not value:
            raise ValueError(f"Environment variable {name} not set")
        return value

    def _fetch_deployment_environments(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }
        url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{self.repo_slug}/environments"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()['values']
        else:
            print(f"Failed to fetch deployment environments: {response.text}")
            return []

    def _fetch_environment_variables(self, environment_uuid):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }
        url = f"https://api.bitbucket.org/2.0/repositories/{self.workspace}/{self.repo_slug}/deployments_config/environments/{environment_uuid}/variables/?page=1&pagelen=100"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()['values']
        else:
            print(f"Failed to fetch environment variables: {response.text}")
            return []

    def update_env_file(self, env_file_path):
        print(f"Updating environment variables in {env_file_path}")
        existing_vars = EnvFileManager.load_env_vars(env_file_path)
        environments = self._fetch_deployment_environments()
        print(f"Found {len(environments)} environments")
        print(f"Looking for environment {self.target_env}")
        updated = False
        for environment in environments:
            print(f"Checking environment {environment['name']}")
            if environment['name'].lower() == self.target_env.lower():
                print(f"Updating environment variables for {environment['name']}")
                variables = self._fetch_environment_variables(environment['uuid'])    
                print(f"Found {len(variables)} variables")
                for var in variables:
                    env_var_key = f"{var['key']}"
                    if env_var_key in existing_vars:
                        if var['secured']:
                            print(f"failed variable {env_var_key} is secured, can not get value.")
                            exit(1)
                        existing_vars[env_var_key] = var['value']
                        updated = True
        
        if updated:
            EnvFileManager.save_env_vars(existing_vars, env_file_path)
            print("Environment variables updated successfully.")
        else:
            print("No updates were made to the environment variables.")
            exit(1)
