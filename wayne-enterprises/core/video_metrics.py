from dataclasses import dataclass
from datetime import datetime

@dataclass
class VideoMetrics:
    """Data class to store video metrics and metadata"""
    video_id: str
    title: str
    description: str
    published_at: datetime
    duration: str
    view_count: int
    like_count: int
    comment_count: int
    tags: list
    topic: str
    engagement_rate: float = 0.0
