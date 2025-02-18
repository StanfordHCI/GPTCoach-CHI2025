# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

import os
import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin import firestore, firestore_async
from google.cloud.firestore_v1 import DocumentReference

STUDY_ID = "testing"
FIREBASE_PROJECT_NAME = ""

# Parse environment variable to set the flag for using firebase emulator
def str_to_bool(value):    
    if value.lower() in {'true', 't', '1', 'yes', 'y'}:
        return True
    return False

PROD = str_to_bool(os.getenv('PROD', 'False'))

if PROD:    
    USE_EMULATOR = False
else:
    USE_EMULATOR = True

class FirebaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
            # Initialize attributes
            cls._instance.app = None
            cls._instance.db = None
            cls._instance.async_db = None
            cls._instance.auth = None
        return cls._instance

    def initialize_firebase_app(self):
        if USE_EMULATOR:
            print("Initializing Firebase with emulator environment")
            os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
            os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = "localhost:9099"
            self.db = firestore.Client(project=FIREBASE_PROJECT_NAME)
            self.async_db = firestore_async.AsyncClient(project=FIREBASE_PROJECT_NAME)
            self.app = firebase_admin.initialize_app()
        else:
            print("Initializing Firebase with production environment")
            cred = credentials.Certificate('serviceAccount.json')
            self.app = firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            self.async_db = firestore_async.client()
            self.async_db = firestore_async.client()

        self.auth = auth
        return self

    def get_users_col(self, async_ref=False):
        # Returns a reference to the users collection in firebase
        if not async_ref:
            return self.db.collection(f'studies/{STUDY_ID}/users')
        else:
            return self.async_db.collection(f'studies/{STUDY_ID}/users')

    def get_user_doc(self, user_id: str, async_ref=False) -> DocumentReference:
        # Returns a reference to a user's document in firebase
        # Raises an error if user is not found
        if not async_ref:
            user_doc_ref = self.db.collection(f'studies/{STUDY_ID}/users').document(user_id)
        else:
            user_doc_ref = self.async_db.collection(f'studies/{STUDY_ID}/users').document(user_id)

        if not self.is_valid_user_id(user_id):
            raise ValueError(f"User {user_id} not found")
        
        return user_doc_ref

    def is_valid_user_id(self, user_id: str) -> bool:
        # Returns true if the user id is valid, false otherwise
        user_doc_ref = self.db.collection(f'studies/{STUDY_ID}/users').document(user_id)
        user_doc = user_doc_ref.get()
        return user_doc.exists
    
    def verify_token(self, token: str) -> str:
        # Verify the token and return the user id
        decoded_token = self.auth.verify_id_token(token)
        return decoded_token['uid']
    
    def get_root_path(self):
        return f'studies/{STUDY_ID}'