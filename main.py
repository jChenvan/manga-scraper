import time
from playwright.sync_api import sync_playwright, Page

def get_largest_img(images):
    largest_img = {
        "size": 0,
        "element": None
    }

    for img in images:
        img_size = img.evaluate("img => img.naturalWidth * img.naturalHeight")
        if img_size > largest_img["size"]:
            largest_img["size"] = img_size
            largest_img["element"] = img

    return largest_img["element"]

def download_page(page: Page, last_visited):
    last_visited["page-number"] += 1
    page_number = last_visited["page-number"]

    images = page.query_selector_all("img")

    largest = get_largest_img(images)

    src = largest.get_attribute("src")

    if src == last_visited.get("img-src"):
        return True

    if not src:
        print(f"No valid image found on page {page_number}.")
    else:
        image_data = page.request.get(src).body()
        with open(f"pages/page_{page_number:03}.jpg", "wb") as f:
            f.write(image_data)

    last_visited["url"] = page.url
    last_visited["title"] = page.title()
    last_visited["img-src"] = src

    return False

def main():
    first_page_url = input(">> Url of first page: ").strip()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(first_page_url)
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        last_visited = {
            "url": None,
            "title": None,
            "img-src": None,
            "page-number": 0
        }

        while True:
            done = download_page(page, last_visited)
            if done:
                break

            page.press("body", "ArrowRight")
            page.wait_for_load_state("networkidle")
            time.sleep(1)

if __name__ == "__main__":
    main()