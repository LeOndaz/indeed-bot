. .\venv\Scripts\activate
start-process powershell {uvicorn server:app --reload}
cd frontend
npm start
