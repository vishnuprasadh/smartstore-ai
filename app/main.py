from fastapi import FastAPI
from app.schemas.product import Product

app = FastAPI(
    title = "SmartStore AI",
    description = "Retail intelligence and recommendation platform",
    version="1.0"
)

@app.get("/")
def root():
    return {
        "application":"SmartStore AI",
        "status": "running"   
    }


@app.get("/health")
def health_check():
    return{
            "status":"healthy"
    }


@app.get("/products", response_model=list[Product])
def getproducts():
    return [
            {
                "id":"P1001",
                "name":"iPhone 17",
                "price":"79900",
                "currency":"INR"
            },
            {
                "id":"P1002",
                "name":"Samsung Galaxy S25",
                "price":"74999",
                "currency":"INR"
            },
            {
                "id":"P1003",
                "name":"MacBook Air",
                "price":"99900",
                "currency":"INR"
            }
    ]