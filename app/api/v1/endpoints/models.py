import time

from app.api.deps import get_current_approved_user
from app.gpt.gpthf import GPTHF
from app.gpt.models import gpt_models
from app.schemas.model_item import ModelGenRequest, ModelLoadRequest
from app.schemas.user import User
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()


@router.get("/")
async def get_model_list():
    model_dict = {"models": {}}

    for model in gpt_models:
        model_dict["models"][model.model_name] = {"ready": True}

    return model_dict


@router.post("/load")
async def load_model(request: ModelLoadRequest, current_user: User = Depends(get_current_approved_user)): # noqa
    # Check that model exists
    if gpt_models is not None:
        for m in gpt_models:
            if m.model_name == request.model:
                raise HTTPException(status_code=400, detail="Model already loaded")

    try:
        model = GPTHF(model_name=request.model, parallelize=request.parallel, sharded=request.sharded)
        gpt_models.append(model)

        return {f"Successfully loaded model: {request.model}"}

    except Exception as e:
        return HTTPException(status_code=400, detail=f"Unsupported model type: {request.model}\n{e}")


@router.post("/generate")
async def generate(request: ModelGenRequest, current_user: User = Depends(get_current_approved_user)): # noqa
    for m in gpt_models:
        if m.model_name == request.model:
            try:
                return {"completion": {
                    "text": m.generate(request.dict()),
                    "time": time.time()
                }}

            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid request body!\n{e}")

    raise HTTPException(status_code=404, detail="Model not found.")
