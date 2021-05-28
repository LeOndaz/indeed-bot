from fastapi import FastAPI, BackgroundTasks, WebSocket, HTTPException
from pydantic import BaseModel
# from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.cors import CORSMiddleware
import indeed
from typing import List


class IndeedFormData(BaseModel):
    email: str
    password: str
    what: str
    where: str


app = FastAPI()

allowed_hosts = [
    'http://localhost:3000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_hosts,
    allow_credentials=True,
    allow_methods=['POST'],
    allow_headers=['*'],
)


@app.post('/run/')
def home_page(data: IndeedFormData, background_tasks: BackgroundTasks):
    background_tasks.add_task(indeed.start_applying, data.email, data.password, data.what, data.where)

    return {
        'message': 'Added a new task.',
    }


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket('/ws/automate/{id}')
async def handle_automate(socket: WebSocket, id: str):
    await manager.connect(socket)

    async def get_2fa_code():
        await socket.send_json({
            'event': 'code',
        })
        data = await socket.receive_json()
        return data.get('data').get('code')

    while True:
        data = await socket.receive_json()
        action = data.get('action', None)
        data = data.get('data', None)

        if not all([action, data]):
            await socket.close(1002)

        if action == 'start':
            email, password = data.get('email'), data.get('password')
            what, where = data.get('what'), data.get('where')

            driver = indeed.setup_webdriver()
            procedure = indeed.IndeedAutomationProcedure(driver, id=id)
            await procedure.start(what=what, where=where, email=email, password=password, get_2fa_code=get_2fa_code)

