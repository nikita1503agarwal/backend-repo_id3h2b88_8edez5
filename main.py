import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Company, Loan, Drawdown, Repayment

app = FastAPI(title="External Loans Portal API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "External Loans Portal Backend Running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            try:
                response["collections"] = db.list_collection_names()[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


# --------- Helpers ---------

def str_id(obj):
    if isinstance(obj, dict) and obj.get("_id"):
        obj["_id"] = str(obj["_id"])  # type: ignore
    return obj


def to_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")


# --------- Company Endpoints ---------

@app.post("/companies", response_model=dict)
def create_company(payload: Company):
    new_id = create_document("company", payload)
    return {"_id": new_id}


@app.get("/companies", response_model=List[dict])
def list_companies():
    docs = get_documents("company")
    return [str_id(d) for d in docs]


# --------- Loans Endpoints ---------

class LoanIn(Loan):
    pass

@app.post("/loans", response_model=dict)
def create_loan(payload: LoanIn):
    # Validate company exists
    company_oid = to_object_id(payload.company_id)
    if not db["company"].find_one({"_id": company_oid}):
        raise HTTPException(status_code=404, detail="Company not found")
    new_id = create_document("loan", payload)
    return {"_id": new_id}


@app.get("/loans", response_model=List[dict])
def list_loans(company_id: Optional[str] = None):
    q = {}
    if company_id:
        q["company_id"] = company_id
    docs = get_documents("loan", q)
    return [str_id(d) for d in docs]


# --------- Drawdowns (Tirages) ---------

class DrawdownIn(Drawdown):
    pass

@app.post("/drawdowns", response_model=dict)
def create_drawdown(payload: DrawdownIn):
    # Validate loan exists
    loan_oid = to_object_id(payload.loan_id)
    if not db["loan"].find_one({"_id": loan_oid}):
        raise HTTPException(status_code=404, detail="Loan not found")
    new_id = create_document("drawdown", payload)
    return {"_id": new_id}


@app.get("/drawdowns", response_model=List[dict])
def list_drawdowns(loan_id: Optional[str] = None):
    q = {}
    if loan_id:
        q["loan_id"] = loan_id
    docs = get_documents("drawdown", q)
    return [str_id(d) for d in docs]


# --------- Repayments ---------

class RepaymentIn(Repayment):
    pass

@app.post("/repayments", response_model=dict)
def create_repayment(payload: RepaymentIn):
    # Validate loan exists
    loan_oid = to_object_id(payload.loan_id)
    if not db["loan"].find_one({"_id": loan_oid}):
        raise HTTPException(status_code=404, detail="Loan not found")
    new_id = create_document("repayment", payload)
    return {"_id": new_id}


@app.get("/repayments", response_model=List[dict])
def list_repayments(loan_id: Optional[str] = None, planned: Optional[bool] = None):
    q = {}
    if loan_id:
        q["loan_id"] = loan_id
    if planned is not None:
        q["planned"] = planned
    docs = get_documents("repayment", q)
    return [str_id(d) for d in docs]


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
