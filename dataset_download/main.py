import kagglehub
import os
import shutil
# from kagglehub import KaggleDatasetAdapter

datasets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datasets")

# path = kagglehub.dataset_download("saurabhbagchi/books-dataset")
# shutil.move(path, datasets_path)

# path = kagglehub.dataset_download("manann/quotes-500k")
# shutil.move(path, datasets_path)

# path = kagglehub.dataset_download("akmittal/quotes-dataset")
# shutil.move(path, datasets_path)

path = kagglehub.dataset_download("dwsstudio/scrapped-quotes")
shutil.move(path, datasets_path)
