from fastapi import FastAPI, WebSocket
import uvicorn

app = FastAPI()
clients = []   # список подключенных клиентов

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
    print("User connected!")

    while True:
        try:
            data = await ws.receive_text()

            # Рассылаем всем клиентам
            for client in clients:
                await client.send_text(data)

        except:
            clients.remove(ws)
            print("User disconnected!")
            break


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5555)
