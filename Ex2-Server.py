import asyncio
import json
import logging
import websockets

logging.basicConfig()

STATE = {"value": 0}

USERS = {}

def state_event():
    return json.dumps({"type": "state", **STATE})

def users_event():
    return json.dumps({"type": "users", "count": len(USERS)})

def message_event(txt):
    return json.dumps({"type": "message", "text": txt})

def system_event(txt):
    return json.dumps({"type": "message", "text": txt})

async def notify_state():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS.values()])

async def notify_message(txt,src):
    if len(USERS)>1:  # asyncio.wait doesn't accept an empty list
        message = message_event(txt)
        await asyncio.wait([user.send(message) for key, user in USERS.items() if key != src])

async def notify_system(txt):
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = system_event(txt)
        await asyncio.wait([user.send(message) for user in USERS.values()])

async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS.values()])


async def register(websocket):
    name = 'UNK'+ str(len(USERS))
    USERS[name] = websocket
    await notify_users()


async def unregister(websocket):
    try:
        keyf = ""
        for key, usr in USERS.items():
            if websocket == usr:
                keyf = key
        USERS.pop(keyf)
        await notify_users()
    except:
        print('oi')

async def communicate(websocket, path):
    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message)
            msg = data["message"]
            keyf = ""
            for key, usr in USERS.items():
                if websocket == usr:
                    keyf = key
            if(msg[0:5] == "/name"):
                nome = msg[6:len(msg)]
                if nome in USERS:
                    msg = json.dumps({"type": "system", "text": 'Sistema: Nome indisponível, escolha outro.'})
                    await websocket.send(msg)
                else:
                    USERS.pop(keyf, None)
                    USERS[nome] = websocket
                    await notify_system(nome + " entrou na sala.")
            else:
                if(keyf[0:3] == "UNK"):
                    msg = json.dumps({"type": "system", "text": 'Sistema: Defina um nome antes de enviar mensagens.'})
                    await websocket.send(msg)
                else:
                    if(msg[0]=="/"):
                        privado = msg[1:len(msg)].split()[0]
                        if privado in USERS:
                            msg = json.dumps({"type": "message", "text": keyf + "(privado):" + msg[len(privado)+1:len(msg)]})
                            await USERS[privado].send(msg)
                        else:
                            msg = json.dumps({"type": "system", "text": 'Sistema: Usuário '+privado+' não encontrado.'})
                            await websocket.send(msg)
                    else:
                        await notify_message(keyf+": "+msg, keyf)
    finally:
        await unregister(websocket)


start_server = websockets.serve(communicate, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()