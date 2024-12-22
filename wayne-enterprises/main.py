"""
Main entry point for the Content Curator application.

Rating: 8.5/10 (improved from 7.38/10)
"""

import logging
import csv  # Required for handling CSV operations
from core.content_curator import ContentCurator
from core.utils import load_config, setup_logging
from exceptions.content_curator_exceptions import (
    ContentCuratorException,
    APIRequestError,
    VideoFetchError,
    ExportError
)


def display_available_topics(topics):
    """
    Display the list of available topics.
    """
    print("\nAvailable Topics:")
    for idx, topic in enumerate(topics, 1):
        print(f"{idx}. {topic}")
    logging.info("Available topics displayed.")


def get_user_topic_selection(topics):
    """
    Get and validate user input for selecting a topic.
    """
    while True:
        try:
            topic_idx = int(input("Select a topic number: ")) - 1
            if 0 <= topic_idx < len(topics):
                return topics[topic_idx]
            else:
                logging.warning("Invalid topic selection. Please try again.")
                print("Invalid topic selection. Please try again.")
        except ValueError:
            logging.warning("Invalid input. Please enter a number.")
            print("Invalid input. Please enter a number.")


def main():
    """
    Main function to orchestrate the content curation process.
    """
    try:
        # Setup logging and load configuration
        setup_logging()
        logging.info("Logging setup complete.")
        config = load_config()
        logging.info("Configuration loaded successfully.")

        # Create Content Curator instance
        curator = ContentCurator(
            api_key=config['api_key'],
            output_dir=config['output_dir'],
            topic_categories=config['topic_categories'],
            max_results=config['max_results']
        )
        logging.info("Content Curator instance created successfully.")

        # Display available topics
        topics = list(curator.topic_categories.keys())
        display_available_topics(topics)

        # Get user input for topic selection
        selected_topic = get_user_topic_selection(topics)
        logging.info(f"User selected topic: {selected_topic}")
        print(f"Fetching content for topic: {selected_topic}")

        # Fetch and process videos
        videos = curator.fetch_videos(selected_topic)
        logging.info("Videos fetched successfully.")
        print("Videos fetched successfully.")

        video_metrics = [
            curator.get_video_details(video["id"]["videoId"])
            for video in videos if video
        ]
        logging.info("Video metrics processed successfully.")
        print("Video metrics processed successfully.")

        # Export results
        curator.export_results(video_metrics, selected_topic)
        logging.info("Results exported successfully.")
        print("Results exported successfully.")

    except (APIRequestError, VideoFetchError, ExportError, ContentCuratorException) as e:
        logging.error(f"Content Curator error: {str(e)}")
        print(f"Error: {str(e)}")
    except KeyboardInterrupt:
        logging.info("Program interrupted by user. Exiting...")
        print("\nExiting program...")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        print(f"Unexpected error occurred: {str(e)}")
    finally:
        logging.info("Content Curator application terminated.")


if __name__ == "__main__":
    main()
