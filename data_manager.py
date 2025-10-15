
import json
import os
import threading

class DataManager:
    def __init__(self, db_dir):
        self.db_dir = db_dir
        os.makedirs(self.db_dir, exist_ok=True)
        self.locks = {}

    def _get_file_path(self, table_name):
        return os.path.join(self.db_dir, f'{table_name}.json')

    def _get_lock(self, table_name):
        if table_name not in self.locks:
            self.locks[table_name] = threading.Lock()
        return self.locks[table_name]

    def _read_data(self, table_name):
        file_path = self._get_file_path(table_name)
        if not os.path.exists(file_path):
            return []
        with self._get_lock(table_name):
            with open(file_path, 'r') as f:
                return json.load(f)

    def _write_data(self, table_name, data):
        file_path = self._get_file_path(table_name)
        with self._get_lock(table_name):
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)

    def get_all(self, table_name):
        return self._read_data(table_name)

    def get_by_id(self, table_name, item_id):
        data = self._read_data(table_name)
        return next((item for item in data if item.get('id') == item_id), None)

    def add(self, table_name, item):
        data = self._read_data(table_name)
        new_id = 1
        if data:
            new_id = max(item.get('id', 0) for item in data) + 1
        item['id'] = new_id
        data.append(item)
        self._write_data(table_name, data)
        return item

    def update(self, table_name, item_id, updates):
        data = self._read_data(table_name)
        for i, item in enumerate(data):
            if item.get('id') == item_id:
                item.update(updates)
                self._write_data(table_name, data)
                return item
        return None

    def delete(self, table_name, item_id):
        data = self._read_data(table_name)
        original_len = len(data)
        data = [item for item in data if item.get('id') != item_id]
        if len(data) < original_len:
            self._write_data(table_name, data)
            return True
        return False

    def find_by_attribute(self, table_name, attribute, value):
        data = self._read_data(table_name)
        return [item for item in data if item.get(attribute) == value]

    def _validate_foreign_key(self, ref_table, ref_id):
        if not self.get_by_id(ref_table, ref_id):
            raise ValueError(f"Foreign key constraint failed: ID {ref_id} not found in {ref_table}")

    def add_with_validation(self, table_name, item, foreign_keys=None, unique_fields=None):
        if foreign_keys:
            for fk_table, fk_id_field in foreign_keys.items():
                self._validate_foreign_key(fk_table, item.get(fk_id_field))

        if unique_fields:
            data = self._read_data(table_name)
            for field in unique_fields:
                if any(d.get(field) == item.get(field) for d in data):
                    raise ValueError(f"Unique constraint failed: {field} '{item.get(field)}' already exists in {table_name}")
        
        return self.add(table_name, item)

    def update_with_validation(self, table_name, item_id, updates, foreign_keys=None, unique_fields=None):
        if foreign_keys:
            for fk_table, fk_id_field in foreign_keys.items():
                if fk_id_field in updates:
                    self._validate_foreign_key(fk_table, updates.get(fk_id_field))

        if unique_fields:
            data = self._read_data(table_name)
            for field in unique_fields:
                if field in updates:
                    if any(d.get(field) == updates.get(field) and d.get('id') != item_id for d in data):
                        raise ValueError(f"Unique constraint failed: {field} '{updates.get(field)}' already exists in {table_name}")

        return self.update(table_name, item_id, updates)


