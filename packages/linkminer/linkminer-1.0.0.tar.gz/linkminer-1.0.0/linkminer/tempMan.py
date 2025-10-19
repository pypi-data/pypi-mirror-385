import tempfile
import os


class TempFileManager:
    def __enter__(self):
        self.temp_file = tempfile.NamedTemporaryFile(
            delete=False, mode="w", suffix=".txt"
        )
        print(f"Temporary file created at: {self.temp_file.name}")
        return self.temp_file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.temp_file.close()
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
            print(f"Temporary file deleted: {self.temp_file.name}")


def read_temp_file(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    return content


def write_temp_file(file_path, content):
    with open(file_path, "w") as file:
        file.write(content)
    return True
