# /root/.cache/kagglehub/datasets/jealousleopard/goodreadsbooks/versions/2/books.csv

import kagglehub
from kagglehub import KaggleDatasetAdapter

# Download latest version
path = kagglehub.dataset_download("saurabhbagchi/books-dataset")
# Set the path to the file you'd like to load
file_path = "books.csv"

# Load the latest version
df = kagglehub.load_dataset(
  KaggleDatasetAdapter.PANDAS,
  "jealousleopard/goodreadsbooks",
  file_path,
  # Provide any additional arguments like 
  # sql_query or pandas_kwargs. See the 
  # documenation for more information:
  # https://github.com/Kaggle/kagglehub/blob/main/README.md#kaggledatasetadapterpandas
)
print("Path to dataset files:", path)