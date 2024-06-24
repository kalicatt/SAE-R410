import asyncio
import signal
from nats.aio.client import Client as NATS

# Configuration de connexion avec timeout augmenté
async def run_nats_client():
    nc = NATS()
    await nc.connect("nats://localhost:4222", connect_timeout=10)

    print("Connecté au serveur NATS")

    # Ajoutez votre logique ici

    await nc.close()

async def shutdown(loop, signal=None):
    if signal:
        print(f"Signal de sortie reçu {signal.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    print(f"Annulation de {len(tasks)} tâches en cours")
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

def handle_signal(loop, sig):
    print(f"Signal reçu: {sig.name}")
    asyncio.create_task(shutdown(loop, sig))

def run_nats_tasks():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    tasks = [
        loop.create_task(run_nats_client())
    ]
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda sig, frame: handle_signal(loop, sig))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Interrompu par l'utilisateur")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
    finally:
        loop.run_until_complete(shutdown(loop))
        loop.close()
        print("Script arrêté proprement")

if __name__ == "__main__":
    run_nats_tasks()
