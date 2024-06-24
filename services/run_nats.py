import asyncio
import signal
import sys
from nats_client import run_login_signup
from nats_departures import run_departures
from nats_arrivals import run_arrivals
from nats_reservation import run_reservations
from nats_admin import run_check_admin

async def shutdown(loop, signal=None):
    """
    Nettoyer les tâches liées à l'arrêt du service.

    Cette fonction est appelée lorsqu'un signal d'arrêt (SIGINT ou SIGTERM) est reçu.
    Elle annule toutes les tâches en cours, attend leur annulation complète et arrête
    la boucle d'événements asyncio.

    Parameters:
    loop (asyncio.AbstractEventLoop): La boucle d'événements asyncio.
    signal (signal.Signals, optional): Le signal reçu déclenchant l'arrêt.
    """
    if signal:
        print(f"Signal de sortie reçu {signal.name}...")

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    print(f"Annulation de {len(tasks)} tâches en cours")
    [task.cancel() for task in tasks]

    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

def run_nats_tasks():
    """
    Exécute les tâches NATS.

    Cette fonction crée une boucle d'événements asyncio et démarre plusieurs tâches NATS
    pour la gestion de l'inscription, des départs, des arrivées et des réservations.
    Elle ajoute également des gestionnaires pour les signaux SIGINT et SIGTERM afin de
    permettre une fermeture propre du script.
    """
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(run_login_signup()),
        loop.create_task(run_departures()),
        loop.create_task(run_arrivals()),
        loop.create_task(run_reservations()),
        loop.create_task(run_check_admin()),
    ]

    if sys.platform == "win32":
        # Windows does not support loop.add_signal_handler
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, lambda s=sig: asyncio.create_task(shutdown(loop, s)))
    else:
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda sig=sig: asyncio.create_task(shutdown(loop, sig)))

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
    """
    Point d'entrée du script.

    Cette section vérifie si le script est exécuté en tant que programme principal
    et appelle la fonction run_nats_tasks pour démarrer les tâches NATS.
    """
    run_nats_tasks()
