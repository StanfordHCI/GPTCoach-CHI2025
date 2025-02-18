# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

from fastapi import APIRouter, HTTPException, Header
from firebase import FirebaseManager

router = APIRouter(prefix="/firebase") 

firebase_manager = FirebaseManager()

@router.get("/status")
async def get_firebase_status() -> str:
    # API endpoint to check if Firebase is initialized
    if not firebase_manager:
        raise HTTPException(status_code=500, detail="Firebase not initialized")
    return "Firebase is initialized"

# generate custom token from user id token API endpoint
@router.get("/verify")
# API endpoint to expose `firebase.verify_token`
async def verify_token(authorization: str = Header(None)) -> str:
    if not authorization:
        raise HTTPException(status_code=400, detail="Authorization header is missing")
    token = authorization.split(" ")[1]

    if not firebase_manager or not firebase_manager.auth:
        raise HTTPException(status_code=500, detail="Firebase not initialized")
    try:
        print("Verifying token:", token)
        uid = firebase_manager.verify_token(token)
        print("Token verified successfully, uid = ", uid)
        return uid
    except Exception as e:  
        raise HTTPException(status_code=401, detail=str(e))
    