from fastapi import FastAPI, BackgroundTasks, WebSocket
from pydantic import BaseModel
# from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.cors import CORSMiddleware
from utils import ConnectionManager
import indeed


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

manager = ConnectionManager()


@app.websocket('/ws/start_instance')
async def handle_automate(socket: WebSocket):
    await manager.connect(socket)

    async def get_2fa_code():
        await socket.send_json({
            'event': 'code',
        })
        data = await socket.receive_json()
        return data.get('data').get('code')

    while True:
        data = await socket.receive_json()

        data = data.get('data', None)
        event = data.get('event', None)

        if not all([event, data]):
            await socket.close(1002)

        if event == 'start':
            body = data.get('body')
            email, password = body.get('email'), body.get('password')
            what, where = body.get('what'), body.get('where')

            driver = indeed.setup_webdriver()
            procedure = indeed.IndeedAutomationProcedure(driver)

            await procedure.start(what=what, where=where, email=email, password=password, get_2fa_code=get_2fa_code)

