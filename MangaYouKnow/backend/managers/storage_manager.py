from backend.models import Data, Chapter


class StorageManager:
    def __init__(self):
        self.data = {}

    def get_data(self, data: Data) -> list[str] | list[Chapter] | bool:
        data_tuple = (data.id, data.model, data.source) if not data.language \
             else (data.id, data.model, data.source, data.language)
        if data_tuple in self.data:
            return self.data[data_tuple].data
        return False
    
    def add_data(self, data: Data) -> None:
        data_tuple = (data.id, data.model, data.source) if not data.language \
             else (data.id, data.model, data.source, data.language)
        self.data[data_tuple] = data

    def remove_data(self, data: Data) -> None:
        data_tuple = (data.id, data.model, data.source) if not data.language \
             else (data.id, data.model, data.source, data.language)
        if data_tuple in self.data:
            del self.data[data_tuple]

    def is_ten_minutes_old(self, data: Data) -> bool:
        data_tuple = (data.id, data.model, data.source) if not data.language \
             else (data.id, data.model, data.source, data.language)
        if data_tuple not in self.data:
            return True
        if self.data[data_tuple].is_ten_minutes_old():
            self.remove_data(data)
            return True
        return False
    