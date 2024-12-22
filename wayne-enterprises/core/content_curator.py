import logging
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import quote_plus
import requests
import csv  # Add this import
from .video_metrics import VideoMetrics
from .utils import load_config, setup_logging

class ContentCurator:
    def __init__(self, api_key, output_dir, topic_categories, max_results):
        self.api_key = api_key
        self.output_dir = Path(output_dir)
        self.topic_categories = topic_categories
        self.max_results = max_results
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_topic_keywords(self, topic: str) -> List[str]:
        return self.topic_categories.get(topic.lower(), [topic])

    def fetch_videos(self, topic: str) -> List[Dict]:
        videos = []
        keywords = self.get_topic_keywords(topic)
        for keyword in keywords:
            try:
                params = {
                    "key": self.api_key,
                    "q": quote_plus(keyword),
                    "part": "snippet",
                    "type": "video",
                    "order": "relevance",
                    "maxResults": self.max_results,
                    "relevanceLanguage": "en",
                    "publishedAfter": (datetime.utcnow() - timedelta(days=30)).isoformat() + "Z"
                }
                response = requests.get(f"{self.base_url}/search", params=params)
                response.raise_for_status()
                videos.extend(response.json().get("items", []))
                time.sleep(0.5)
            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching videos for keyword '{keyword}': {str(e)}")
                continue
        return videos[:self.max_results]

    def get_video_details(self, video_id: str) -> Optional[VideoMetrics]:
        try:
            params = {
                "key": self.api_key,
                "id": video_id,
                "part": "snippet,contentDetails,statistics"
            }
            response = requests.get(f"{self.base_url}/videos", params=params)
            response.raise_for_status()
            video_data = response.json().get("items", [])[0]
            return VideoMetrics(
                video_id=video_id,
                title=video_data["snippet"]["title"],
                description=video_data["snippet"]["description"],
                published_at=datetime.fromisoformat(video_data["snippet"]["publishedAt"].replace('Z', '+00:00')),
                duration=video_data["contentDetails"]["duration"],
                view_count=int(video_data["statistics"].get("viewCount", 0)),
                like_count=int(video_data["statistics"].get("likeCount", 0)),
                comment_count=int(video_data["statistics"].get("commentCount", 0)),
                tags=video_data["snippet"].get("tags", []),
                topic=video_data["snippet"].get("categoryId", "Unknown")
            )
        except Exception as e:
            logging.error(f"Error fetching details for video {video_id}: {str(e)}")
            return None

    def export_results(self, videos, topic):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = self.output_dir / f"{topic}_report_{timestamp}.csv"
        json_path = self.output_dir / f"{topic}_report_{timestamp}.json"
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Video ID", "Title", "Published Date", "Views", "Likes", "Comments", "Engagement Rate", "Tags"])
                for video in videos:
                    writer.writerow([video.video_id, video.title, video.published_at, video.view_count, video.like_count, video.comment_count, f"{video.engagement_rate:.2f}%", ", ".join(video.tags)])
            logging.info(f"CSV report exported to {csv_path}")
        except IOError as e:
            logging.error(f"Error writing CSV file: {str(e)}")

        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump([vars(v) for v in videos], f, default=str, indent=2)
            logging.info(f"JSON report exported to {json_path}")
        except IOError as e:
            logging.error(f"Error writing JSON file: {str(e)}")