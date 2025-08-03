from fetch_data import fetch_all, fetch

result = fetch_all("http://localhost:8080/api/v1/books/")

print(result)