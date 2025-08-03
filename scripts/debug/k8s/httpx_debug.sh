python -c "import httpx, pandas as pd; fetch_all=lambda url,timeout=30:(lambda f:f(f,[],url))(lambda self,r,n:(r.extend((d:=httpx.get(n,timeout=timeout).json()).get('results',[])) or (self(self,r,d.get('next')) if d.get('next') else r))); print(fetch_all('http://book-service:8000/api/v1/books/'))"


python -c "import httpx, pandas as pd; fetch=lambda url,timeout=30: pd.DataFrame(httpx.get(url, timeout=timeout).json()); print(fetch('http://book-service:8000/api/v1/books/'))"

curl http://localhost:8080/api/v1/recommendations/user/276729