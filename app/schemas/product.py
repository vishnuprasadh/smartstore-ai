from pydantic import BaseModel,Field, field_validator

class Product(BaseModel):
    id:str= Field(min_length=1)
    name:str = Field(min_length=1)
    price:float = Field (gt=0)
    currency:str = Field(default="INR")

    @field_validator("currency")
    @classmethod
    def validate_currency(cls,value:str) -> str:
        ccynormalized = value.strip().upper()
        ccyallowed = cls.get_allowedcurrencies()
        if ccynormalized not in ccyallowed:
            raise ValueError(f"Unsupported Currency Value : {value}, Allowed :{sorted(ccyallowed)}")
        return ccynormalized

    @classmethod
    def get_allowedcurrencies(cls) -> set[str]:
        return {"INR", "GBP", "USD", "SGD"}