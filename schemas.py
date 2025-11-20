"""
Database Schemas for External Loans Portal

Each Pydantic model represents a MongoDB collection.
Collection name is the lowercase class name.

- Company -> "company"
- Loan -> "loan"
- Drawdown -> "drawdown"
- Repayment -> "repayment"
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import date as Date

class Company(BaseModel):
    """
    Tunisian company registering external loans
    Collection: company
    """
    name: str = Field(..., description="Company legal name")
    tax_id: str = Field(..., description="Matricule fiscal")
    sector: Optional[str] = Field(None, description="Industry sector")
    contact_email: Optional[EmailStr] = Field(None, description="Contact email")
    contact_phone: Optional[str] = Field(None, description="Contact phone number")

class Loan(BaseModel):
    """
    External loan contracted with a non-resident lender
    Collection: loan
    """
    company_id: str = Field(..., description="Reference to company _id as string")
    lender_name: str = Field(..., description="Non-resident lender name")
    currency: str = Field(..., min_length=3, max_length=3, description="ISO currency code, e.g., EUR, USD")
    principal_amount: float = Field(..., ge=0, description="Original principal amount")
    interest_rate: Optional[float] = Field(None, ge=0, description="Nominal annual interest rate (in %)")
    start_date: Optional[Date] = Field(None, description="Start/Signature date")
    maturity_date: Optional[Date] = Field(None, description="Final maturity date")
    purpose: Optional[str] = Field(None, description="Use of proceeds / purpose")
    status: Literal["active", "repaid", "defaulted", "cancelled"] = Field("active", description="Current status")

class Drawdown(BaseModel):
    """
    Drawdowns (tirages) realized under a loan
    Collection: drawdown
    """
    loan_id: str = Field(..., description="Reference to loan _id as string")
    amount: float = Field(..., gt=0, description="Amount drawn")
    date: Date = Field(..., description="Drawdown date")
    remarks: Optional[str] = Field(None, description="Notes")

class Repayment(BaseModel):
    """
    Repayments executed or planned
    Collection: repayment
    """
    loan_id: str = Field(..., description="Reference to loan _id as string")
    amount: float = Field(..., gt=0, description="Amount paid or planned")
    date: Date = Field(..., description="Payment date (actual or planned)")
    component: Literal["principal", "interest", "fees"] = Field("principal", description="Repayment component")
    planned: bool = Field(False, description="True if scheduled/planned, False if already paid")
