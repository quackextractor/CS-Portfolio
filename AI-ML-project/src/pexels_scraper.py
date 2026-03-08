import os
import requests
import argparse
from dotenv import load_dotenv

load_dotenv()


def download_pexels_images(query: str, total_images: int, output_dir: str) -> None:
    """
    Downloads images from Pexels API based on a query.

    Args:
        query (str): The search query (e.g., 'portrait face').
        total_images (int): Target number of images to download.
        output_dir (str): Directory to save downloaded images.
    """
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        print("Error: PEXELS_API_KEY not found in .env file.")
        return

    os.makedirs(output_dir, exist_ok=True)

    existing_files = [
        f for f in os.listdir(output_dir) if f.startswith("pexels_") and f.endswith(".jpg")
    ]
    total_collected = len(existing_files)

    if total_collected >= total_images:
        print(
            f"Directory already contains {total_collected} images "
            f"(target: {total_images}). Skipping download."
        )
        return

    print(f"Found {total_collected} existing images. Target is {total_images}.")

    headers = {"Authorization": api_key}

    per_page = 80
    page = 1
    new_downloads = 0

    while total_collected < total_images:
        url = f"https://api.pexels.com/v1/search?query={query}&per_page={per_page}&page={page}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Error: API request failed with status code {response.status_code}")
            print(response.text)
            break

        data = response.json()
        photos = data.get("photos", [])

        if not photos:
            print("No more photos found.")
            break

        for photo in photos:
            if total_collected >= total_images:
                break

            filename = os.path.join(output_dir, f"pexels_{photo['id']}.jpg")
            if os.path.exists(filename):
                continue

            img_url = photo["src"]["medium"]
            img_data = requests.get(img_url).content

            with open(filename, "wb") as f:
                f.write(img_data)

            total_collected += 1
            new_downloads += 1
            if new_downloads % 50 == 0:
                print(f"Collected {total_collected}/{total_images} images...")

        page += 1

    print(
        f"Finished. Downloaded {new_downloads} new images "
        f"into {output_dir} (Total: {total_collected})"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download portrait images from Pexels for the negative class."
    )
    parser.add_argument(
        "--query", type=str, default="portrait face", help="Search query for Pexels"
    )
    parser.add_argument(
        "--total", type=int, default=1200, help="Total number of images to download"
    )
    parser.add_argument(
        "--output_dir", type=str, default="data/raw/negative", help="Output directory"
    )

    args = parser.parse_args()
    download_pexels_images(args.query, args.total, args.output_dir)
