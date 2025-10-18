import os
import re
import subprocess
from sefrone_build.builder_utils import EnvFileManager

class DotNetEFCoreDBScaffold:
    def __init__(self):
        self._data_project_dir: str = self._find_data_project_dir()

    def _find_data_project_dir(self)-> str:
        current_dir = os.getcwd()
        for root, dirs, files in os.walk(current_dir):
            for d in dirs:
                if "api.data" in d.lower():
                    return os.path.join(root, d)
        print("Data project directory not found.")
        exit(1)

    def _get_data_folder_name(self, data_project_dir: str) -> str:
        return os.path.basename(data_project_dir)

    def _get_table_names_from_sql(self, file_path):
        table_names = []
        with open(file_path, 'r') as file:
            sql_content = file.read()
            table_creation_pattern = r'CREATE TABLE\s+\"?(\w+)\"?\s*\('
            table_names = re.findall(table_creation_pattern, sql_content, re.IGNORECASE)
        return table_names

    def _execute_postgres_scaffold_command(self, db_connection_string):
        sql_file_path = os.path.join(self._data_project_dir, 'DbSchema', 'Schema', 'init.sql')

        table_names = self._get_table_names_from_sql(sql_file_path)
        
        table_args = ' '.join(f'-t {table_name}' for table_name in table_names)
        
        data_namespace = self._get_data_folder_name(self._data_project_dir).replace("API", "Api")
        scaffold_cmd = (
            f"dotnet ef dbcontext scaffold --no-onconfiguring \"{db_connection_string}\" "
            f"Npgsql.EntityFrameworkCore.PostgreSQL -o Entities -c RestApiDbContext "
            f"--context-dir Entities/Context -f --project {self._data_project_dir} "
            f"--context-namespace {data_namespace} --namespace {data_namespace} --force {table_args}"
        )
        subprocess.run(scaffold_cmd, shell=True)

    def _execute_mysql_scaffold_command(self, db_connection_string):
        sql_file_path = os.path.join(self._data_project_dir, 'DbSchema', 'Schema', 'init.sql')

        table_names = self._get_table_names_from_sql(sql_file_path)
        
        table_args = ' '.join(f'-t {table_name}' for table_name in table_names)
        
        data_namespace = self._get_data_folder_name(self._data_project_dir).replace("API", "Api")
        scaffold_cmd = (
            f"dotnet ef dbcontext scaffold --no-onconfiguring \"{db_connection_string}\" "
            f"Pomelo.EntityFrameworkCore.MySql -o Entities -c RestApiDbContext "
            f"--context-dir Entities/Context -f --project {self._data_project_dir} "
            f"--context-namespace {data_namespace} --namespace {data_namespace} --force {table_args}"
        )
        subprocess.run(scaffold_cmd, shell=True)

    def _append_entity_suffix(self, file_path, sorted_class_mapping):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        for original_class_name, new_class_name in sorted_class_mapping.items():
            content = content.replace(f"<{original_class_name}>", f"<{new_class_name}>")
            content = content.replace(f"public virtual {original_class_name} ", f"public virtual {new_class_name} ")
            content = content.replace(f"public virtual {original_class_name}?", f"public virtual {new_class_name}?")
            content = content.replace(f"public partial class {original_class_name}\n", f"public partial class {new_class_name}\n")

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

    def _rename_classes_and_update_references(self):
        entities_dir = os.path.join(self._data_project_dir, 'Entities')
        context_file = os.path.join(self._data_project_dir, 'Entities', 'Context', 'RestApiDbContext.cs')

        class_mapping = {}

        print("Removing old files with suffix 'Entity'")
        for filename in os.listdir(entities_dir):
            if filename.endswith("Entity.cs"):
                file_path = os.path.join(entities_dir, filename)
                os.remove(file_path)
                
        print(f"Renaming classes in {entities_dir} with suffix 'Entity'")
        for filename in os.listdir(entities_dir):
            if filename.endswith(".cs"):
                file_path = os.path.join(entities_dir, filename)

                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                for line in content.splitlines():
                    if line.startswith("public partial class "):
                        original_class_name = line.split()[3]
                        new_class_name = f"{original_class_name}Entity"
                        class_mapping[original_class_name] = new_class_name
                        break

        sorted_class_mapping = dict(
            sorted(class_mapping.items(), key=lambda item: len(item[0]), reverse=True)
        )

        for filename in os.listdir(entities_dir):
            if filename.endswith(".cs"):
                file_path = os.path.join(entities_dir, filename)

                self._append_entity_suffix(file_path, sorted_class_mapping)
                
        self._append_entity_suffix(context_file, sorted_class_mapping)

        print(f"Renaming files in {entities_dir} with suffix 'Entity'")
        for filename in os.listdir(entities_dir):
            if filename.endswith(".cs"):
                old_path = os.path.join(entities_dir, filename)
                new_filename = filename.replace(".cs", "Entity.cs")
                new_path = os.path.join(entities_dir, new_filename)

                os.rename(old_path, new_path)

    def prepare_and_scaffold_postgres_data_project(self, env_file_path):
        db_connection_string = EnvFileManager.read_env_value(env_file_path, 'SCAFFOLD_DB_CONNECTION_STRING')
        if db_connection_string:
            self._execute_postgres_scaffold_command(db_connection_string)
            self._rename_classes_and_update_references()
        else:
            print(f"SCAFFOLD_DB_CONNECTION_STRING not found in .env file at {env_file_path}.")
            exit(1)

    def prepare_and_scaffold_mysql_data_project(self, env_file_path):
        db_connection_string = EnvFileManager.read_env_value(env_file_path, 'SCAFFOLD_DB_CONNECTION_STRING')
        if db_connection_string:
            self._execute_mysql_scaffold_command(db_connection_string)
            self._rename_classes_and_update_references()
        else:
            print(f"SCAFFOLD_DB_CONNECTION_STRING not found in .env file at {env_file_path}.")
            exit(1)