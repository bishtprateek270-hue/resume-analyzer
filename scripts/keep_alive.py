import sys
import time
from playwright.sync_api import sync_playwright

APP_URL = "https://resume-analyzer-nejevwpy2bcvrvuag9schr.streamlit.app/"

def keep_alive():
    print(f"Launching headless browser to visit {APP_URL}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        try:
            page.goto(APP_URL, wait_until="networkidle", timeout=60000)
            time.sleep(5)
            
            # Check if the Streamlit sleep button is present
            wake_button = page.get_by_role("button", name="Yes, get this app back up!")
            if wake_button.is_visible():
                print("App is currently asleep. Clicking 'Yes, get this app back up!'...")
                wake_button.click()
                print("Clicked wake button. Waiting 45 seconds for app container to boot...")
                time.sleep(45)
            else:
                print("App is already awake and active!")
                
            print(f"Page title: {page.title()}")
            print("Successfully refreshed Streamlit session.")
        except Exception as e:
            print(f"Error during keep-alive execution: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    keep_alive()
