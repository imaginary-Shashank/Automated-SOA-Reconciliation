"""Data schemas and validation models for SOA financial reconciliation."""

from decimal import Decimal, InvalidOperation
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TerminationCharge(BaseModel):
    """Schema representing a single termination charge record from the summary report."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    carrier_name: str = Field(..., min_length=1, description="Raw carrier name from Column A")
    amount: Decimal = Field(..., description="Terminating Bill amount from Column B")
    status: str | None = Field(default=None, description="Status from Column C")
    comment: str | None = Field(default=None, description="Comment from Column D")
    source_row: int = Field(..., description="The Excel row index this record was read from")

    @field_validator("amount", mode="before")
    @classmethod
    def parse_amount(cls, value: object) -> Decimal:
        """Coerce raw input (floats, formatted strings) into precise Decimal values."""
        if value is None:
            raise ValueError("Amount cannot be empty.")
            
        try:
            if isinstance(value, (int, float)):
                return Decimal(str(value))
            if isinstance(value, str):
                # Strip currency symbols or commas if present in Excel formatting
                clean_str = value.replace("$", "").replace(",", "").strip()
                return Decimal(clean_str)
            if isinstance(value, Decimal):
                return value
        except InvalidOperation:
            # Pydantic expects a ValueError to trigger its validation failure correctly
            raise ValueError(f"Could not convert '{value}' into a precise financial amount.")
            
        raise TypeError(f"Unsupported type for amount: {type(value)}")


class ReconciliationBatch(BaseModel):
    """Wrapper holding a batch of validated records ready for Excel ingestion."""

    records: list[TerminationCharge] = Field(default_factory=list)

    @property
    def total_amount(self) -> Decimal:
        """Calculate total batch value deterministically."""
        return sum((record.amount for record in self.records), Decimal("0"))