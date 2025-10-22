import firebase_admin
from firebase_admin import credentials, firestore

def inicializar_firebase():
    """
    Inicializa o Firebase Admin SDK se ainda não foi inicializado.
    """
    if not firebase_admin._apps:
        cred = credentials.Certificate("helpnow-89742-firebase-adminsdk-fbsvc-c93ddd8230.json")
        firebase_admin.initialize_app(cred)
    
    return firestore.client()

db = inicializar_firebase()
