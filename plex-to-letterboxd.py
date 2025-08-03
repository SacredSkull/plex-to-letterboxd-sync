import csv
import os
from plexapi.server import PlexServer
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

# -------- CONFIG ---------
PLEX_URL = os.environ.get('PLEX_URL')
PLEX_TOKEN = os.environ.get('PLEX_TOKEN')
LETTERBOXD_EMAIL = os.environ.get('LETTERBOXD_EMAIL')
LETTERBOXD_PASSWORD = os.environ.get('LETTERBOXD_PASSWORD')
OUTPUT_CSV = "plex_watched_letterboxd.csv"

# -------------------------

required_vars = ['PLEX_URL', 'PLEX_TOKEN', 'LETTERBOXD_EMAIL', 'LETTERBOXD_PASSWORD']
missing_vars = [var for var in required_vars if not os.environ.get(var)]
if missing_vars:
    print("Please set the following environment variables:")
    print(", ".join(missing_vars))
    exit(1)

def get_plex_movies():
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    movies = plex.library.section('Movies')
    watched = []
    for movie in movies.search(unwatched=False):
        # Only add movies with a watched date
        if movie.lastViewedAt:
            # Plex sometimes returns multiple directors
            directors = ", ".join([p.tag for p in movie.directors]) if movie.directors else ""
            watched.append({
                "Title": movie.title,
                "Year": movie.year,
                "Directors": directors,
                "WatchedDate": movie.lastViewedAt.strftime("%Y-%m-%d")
            })
    return watched


def write_letterboxd_csv(movies, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Title", "Year", "Directors", "WatchedDate"])
        writer.writeheader()
        for row in movies:
            writer.writerow(row)


def upload_to_letterboxd(email, password, csv_path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Navigate to Letterboxd import page
        page.goto('https://letterboxd.com/import/')

        # Click login (if not already logged in)
        if page.get_by_role("heading", name="Sign in to Letterboxd").is_visible():
            print("Logging in...")
            # Fill in login
            page.get_by_role("textbox", name="Username").click()
            page.get_by_role("textbox", name="Username").fill(LETTERBOXD_EMAIL)
            page.get_by_role("textbox", name="Password").click()
            page.get_by_role("textbox", name="Password").fill(LETTERBOXD_PASSWORD)
            page.get_by_role("button", name="Sign In").click()

        # Upload CSV
        print("Uploading CSV...")
        with page.expect_file_chooser() as fc_info:
            page.get_by_role("link", name="Select a File").click()
        file_chooser = fc_info.value
        file_chooser.set_files(os.path.abspath(csv_path))

        # Wait for upload preview
        page.wait_for_selector(".icon.icon-matched", timeout=180000)
        page.locator(".icon.icon-matched")

        # Click "Import"
        print("Importing CSV...")
        page.get_by_role("link", name="Import Films").click()

        print("Upload triggered! Please review the import in your browser.")
        # Wait a while before closing
        page.wait_for_timeout(10000)
        browser.close()


def main():
    print("Extracting watched movies from Plex...")
    watched_movies = get_plex_movies()
    print(f"Found {len(watched_movies)} watched movies.")
    print(f"Writing to {OUTPUT_CSV}...")
    write_letterboxd_csv(watched_movies, OUTPUT_CSV)
    print("Uploading CSV to Letterboxd...")
    upload_to_letterboxd(LETTERBOXD_EMAIL, LETTERBOXD_PASSWORD, OUTPUT_CSV)
    print("Done!")


if __name__ == '__main__':
    main()
