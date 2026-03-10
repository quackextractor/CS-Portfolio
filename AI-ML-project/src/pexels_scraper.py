import os
import requests
import argparse
import logging
from dotenv import load_dotenv
from typing import List, Union

load_dotenv()


def download_pexels_images(
    queries: Union[str, List[str]], total_images: int, output_dir: str
) -> None:
    """
    Downloads images from Pexels API based on one or more queries.
    """
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        logging.error("PEXELS_API_KEY not found in .env file.")
        return

    if isinstance(queries, str):
        queries = [queries]

    os.makedirs(output_dir, exist_ok=True)

    num_queries = len(queries)
    target_per_query = total_images // num_queries

    headers = {"Authorization": api_key}
    total_new_downloads = 0

    for query in queries:
        logging.info(f"Processing query: '{query}' (Target: {target_per_query})")

        query_collected = 0
        page = 1
        per_page = 80

        while query_collected < target_per_query:
            url = (
                f"https://api.pexels.com/v1/search?query={query}&"
                f"per_page={per_page}&page={page}"
            )
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    logging.error(
                        f"API request failed for '{query}' (Page {page}): {response.status_code}"
                    )
                    break

                data = response.json()
                photos = data.get("photos", [])
                if not photos:
                    logging.info(f"No more photos for query '{query}'")
                    break

                for photo in photos:
                    if query_collected >= target_per_query:
                        break

                    filename = os.path.join(output_dir, f"pexels_{photo['id']}.jpg")
                    if os.path.exists(filename):
                        continue

                    try:
                        img_data = requests.get(photo["src"]["medium"], timeout=10).content
                        with open(filename, "wb") as f:
                            f.write(img_data)
                        query_collected += 1
                        total_new_downloads += 1
                        if total_new_downloads % 20 == 0:
                            logging.info(f"Downloaded {total_new_downloads} images so far...")
                    except Exception as e:
                        logging.warning(f"Failed to download photo {photo['id']}: {e}")

                page += 1
            except Exception as e:
                logging.error(f"Request error for query '{query}': {e}")
                break

    logging.info(f"Finished. Total new images downloaded: {total_new_downloads}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download portrait images from Pexels for the negative class."
    )
    parser.add_argument(
        "--query",
        type=str,
        nargs="+",
        default=["portrait face"],
        help="Search query or queries for Pexels"
    )
    parser.add_argument(
        "--total", type=int, default=1200, help="Total number of images to download"
    )
    parser.add_argument(
        "--output_dir", type=str, default="data/raw/negative", help="Output directory"
    )

    args = parser.parse_args()
    download_pexels_images(args.query, args.total, args.output_dir)
