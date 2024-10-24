# -*- coding: utf-8 -*-
import os

class Getfiles:
  def __init__(self, path='data/symbols'):
    self.path = path

  def directories(self):
    list_dirs = []
    for item in os.listdir(self.path):
      full_dir_path = os.path.join(self.path, item)
      if os.path.isdir(full_dir_path):
        list_dirs.append(item)

    csv_files = []
    for dir_path in list_dirs:
      full_dir_path = os.path.join(self.path, dir_path)
      for file in os.listdir(full_dir_path):
        if file.startswith('symbols-') and file.endswith('.csv'):
          full_file_path = os.path.join(full_dir_path, file)
          file_mtime = os.path.getmtime(full_file_path)
          csv_files.append((full_file_path, file_mtime))

    return csv_files
