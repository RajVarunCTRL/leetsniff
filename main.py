import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def scrape_paginated_results(base_url, start_page, end_page):
    page_timings = []
    total_users_saved = 0
    auth_file = "auth.json"
    if not os.path.exists(auth_file):
        print("Authfile not found {auth_file}.")
        return
    """
    Scrapes a range of ranking pages and saves the filtered results to a single file.

    Args:
        base_url (str): The contest URL without the page number (e.g., ".../ranking/").
        start_page (int): The first page number to scrape.
        end_page (int): The last page number to scrape.
    """
    with open("results.txt", "w", encoding="utf-8") as f, open("timing_log.txt", "w", encoding="utf-8") as timing_f,  sync_playwright() as p:
        
        browser = p.chromium.launch(headless=True)
        # page = browser.new_page()
        context = browser.new_context(
            storage_state=auth_file,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            )
        page = context.new_page()

        try:
            # main loop for iterating throught the pages.
            for page_num in range(start_page, end_page + 1): 
                # Dynamically construct the URL for the current page
                current_url = f"{base_url}{page_num}/?region=global_v2"
                
                print(f"\n--- Scraping Page: {page_num} ---")
                print(f"URL: {current_url}")
                try:

                    
                    start_time = time.perf_counter()
                    page.goto(current_url, wait_until='domcontentloaded', timeout=7500)
                    
                    # Search for the user using the HTML structure
                    page.locator('div.truncate').first.wait_for(timeout=10000)
                    
                    # Select all user rows on the current page
                    row_selector = 'div.overflow-hidden.min-w-\[fit-content\]:has(div.truncate)'
                    ranking_rows = page.locator(row_selector).all()
                    print(f"Found {len(ranking_rows)} user rows on this page.")

                    # Processing each row found on the page
                    for row in ranking_rows:
                        try:
                            username = row.locator('div.truncate').inner_text()
                            score_text = row.locator('div[class*="max-w-[100px]"]').inner_text()
                            score = int(score_text.strip())

                            if score <= 7:
                                output_line = f"{username} : {score}  : {page_num}\n"
                                f.write(output_line)
                                print(f"Saved: {username} : {score}")
                                total_users_saved+=1

                        except (ValueError, AttributeError):
                            continue # Skip malformed rows
                        
                    # For Logging purposes. 
                    end_time = time.perf_counter()
                    duration_ms = (end_time - start_time) * 1000
                    
                    page_timings.append(duration_ms)
                    timing_f.write(f"{duration_ms:.0f}\n")
                    
                    
                    print(f"-> Page {page_num} processed in {duration_ms:.0f} ms.")

                except (PlaywrightTimeoutError, KeyboardInterrupt):
                    print(f"Page {page_num} timed out or no content found. It might be the last page.")
                    
                    break
                
                # Who needs a time.sleep here?
                # Uncomment the next line if you want to add a delay between page loads
                # time.sleep(0.5)  # Rate Limiting btw.

            print("\nScraping complete. All data saved to results.txt")
            
            context.close()
            browser.close()
            
            if page_timings:
                total_time_sec = sum(page_timings) / 1000
                average_time_ms = sum(page_timings) / len(page_timings)
                pages_per_second = 1000 / average_time_ms if average_time_ms > 0 else 0
                users_per_second = total_users_saved / total_time_sec if total_time_sec > 0 else 0

                print("\n--- Scraping Summary ---")
                print(f"Total pages scraped: {len(page_timings)}")
                print(f"Total users saved (score <= 7): {total_users_saved}") # <-- MODIFIED
                print(f"Total scraping time: {total_time_sec:.2f} seconds")  # <-- NEW
                print(f"Average time per page: {average_time_ms:.0f} ms")
                print(f"Average pages per second: {pages_per_second:.2f}")
                print(f"Average users per second: {users_per_second:.2f}")
                
        except KeyboardInterrupt as e:
            print("Scraping interrupted by user.")

# Set your contest scrape url here.

CONTEST_BASE_URL = "https://leetcode.com/contest/weekly-contest-459/ranking/"


START_PAGE = 490  # Start paeg number where the scrape starts. Adjust as needed.
END_PAGE = 882  # End page number where the scrape ends. Adjust as needed.

# Calling the function :D
scrape_paginated_results(CONTEST_BASE_URL, START_PAGE, END_PAGE)