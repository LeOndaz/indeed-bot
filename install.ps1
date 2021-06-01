start-process powershell {pip install virtualenv; python -m virtualenv venv; .\venv\Scripts\activate; pip install -r requirements.txt} 
cd frontend
npm i
