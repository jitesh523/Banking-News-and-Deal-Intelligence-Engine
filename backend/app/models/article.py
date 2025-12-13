from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Article(BaseModel):
    """Article model for storing news articles."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    article_id: str = Field(..., description="Unique article identifier")
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Article content")
    source: str = Field(..., description="News source")
    author: Optional[str] = Field(None, description="Article author")
    published_date: datetime = Field(..., description="Publication date")
    url: HttpUrl = Field(..., description="Article URL")
    collected_date: datetime = Field(default_factory=datetime.utcnow, description="Collection timestamp")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw API response")
    
    # NLP fields (added in Phase 2)
    entities: Optional[Dict[str, List[str]]] = None
    sentiment: Optional[Dict[str, Any]] = None
    topics: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    processing_date: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "article_id": "newsapi_123456",
                "title": "Major Bank Announces Merger",
                "content": "In a significant development...",
                "source": "Reuters",
                "author": "John Doe",
                "published_date": "2024-01-15T10:30:00Z",
                "url": "https://example.com/article",
            }
        }


class Deal(BaseModel):
    """Deal model for tracking banking deals."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    deal_id: str = Field(..., description="Unique deal identifier")
    deal_type: str = Field(..., description="Type of deal (M&A, IPO, loan, etc.)")
    companies_involved: List[str] = Field(..., description="Companies involved in the deal")
    deal_amount: Optional[float] = Field(None, description="Deal amount in USD")
    announcement_date: datetime = Field(..., description="Deal announcement date")
    status: str = Field(default="announced", description="Deal status")
    related_articles: List[str] = Field(default_factory=list, description="Related article IDs")
    sentiment_impact: Optional[float] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Company(BaseModel):
    """Company model for tracking company information."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    company_id: str = Field(..., description="Unique company identifier")
    name: str = Field(..., description="Company name")
    sector: Optional[str] = Field(None, description="Industry sector")
    relationships: List[Dict[str, Any]] = Field(default_factory=list, description="Company relationships")
    deal_history: List[str] = Field(default_factory=list, description="Deal IDs")
    sentiment_history: List[Dict[str, Any]] = Field(default_factory=list, description="Sentiment over time")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
