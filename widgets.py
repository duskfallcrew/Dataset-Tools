import os
from PyQt6.QtCore import QThread, pyqtSignal


class FileLoader(QThread):
    finished = pyqtSignal(list, list, str)
    progress = pyqtSignal(int)

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self.files = []
        self.images = []
        self.text_files = []

    def run(self):
        self.images, self.text_files = self._scan_directory(self.folder_path)
        self.finished.emit(self.images, self.text_files, self.folder_path)

    def _scan_directory(self, folder_path):
      files = []
      images = []
      text_files = []
      # Gather paths to all files in the selected folder
      try:
          all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)]
      except FileNotFoundError:
          return images, text_files
      total_files = len(all_files)
      progress = 0
      for index, file_path in enumerate(all_files):
        if os.path.isfile(file_path):
          # Filter the file types as needed
          if file_path.lower().endswith(('.png','.jpg','.jpeg','.webp')):
             images.append(file_path)
          if file_path.lower().endswith(('.txt')):
            text_files.append(file_path)
        progress = (index + 1)/total_files * 100
        self.progress.emit(int(progress))
      return images, text_files
    
    def clear_files(self):
       self.files = []