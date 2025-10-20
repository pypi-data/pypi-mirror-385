import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
import pdb

from uk_bin_collection.uk_bin_collection.common import *
from uk_bin_collection.uk_bin_collection.get_bin_data import AbstractGetBinDataClass


# import the wonderful Beautiful Soup and the URL grabber
class CouncilClass(AbstractGetBinDataClass):
    """
    Concrete classes have to implement all abstract operations of the
    base class. They can also override some operations with a default
    implementation.
    """

    def parse_data(self, page: str, **kwargs) -> dict:
        driver = None
        try:
            user_postcode = kwargs.get("postcode")
            if not user_postcode:
                raise ValueError("No postcode provided.")
            check_postcode(user_postcode)

            user_paon = kwargs.get("paon")
            check_paon(user_paon)
            headless = kwargs.get("headless")
            web_driver = kwargs.get("web_driver")
            # Use a realistic user agent to help bypass Cloudflare
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            driver = create_webdriver(web_driver, headless, user_agent, __name__)
            page = "https://www.enfield.gov.uk/services/rubbish-and-recycling/find-my-collection-day"
            driver.get(page)

            # Wait for Cloudflare challenge to complete
            print("Waiting for page to load (Cloudflare check)...")
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    WebDriverWait(driver, 60).until(
                        lambda d: "Just a moment" not in d.title and d.title != "" and len(d.find_elements(By.TAG_NAME, "input")) > 1
                    )
                    print(f"Page loaded: {driver.title}")
                    break
                except:
                    print(f"Attempt {attempt + 1}: Timeout waiting for page load. Current title: {driver.title}")
                    if attempt < max_attempts - 1:
                        time.sleep(10)
                        driver.refresh()
                    else:
                        print("Failed to bypass Cloudflare after multiple attempts")
            
            time.sleep(8)

            try:
                accept_cookies = WebDriverWait(driver, timeout=10).until(
                    EC.presence_of_element_located((By.ID, "ccc-notify-reject"))
                )
                accept_cookies.click()
            except:
                print(
                    "Accept cookies banner not found or clickable within the specified time."
                )
                pass

            # Check for multiple iframes and find the correct one
            try:
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                
                # Try each iframe to find the one with the bin collection form
                for i, iframe in enumerate(iframes):
                    try:
                        driver.switch_to.frame(iframe)
                        
                        # Check if this iframe has the postcode input
                        time.sleep(2)
                        inputs = driver.find_elements(By.TAG_NAME, "input")
                        
                        # Look for address-related inputs
                        for inp in inputs:
                            aria_label = inp.get_attribute('aria-label') or ''
                            placeholder = inp.get_attribute('placeholder') or ''
                            if 'address' in aria_label.lower() or 'postcode' in placeholder.lower():
                                break
                        else:
                            # This iframe doesn't have the form, try the next one
                            driver.switch_to.default_content()
                            continue
                        
                        # Found the right iframe, break out of the loop
                        break
                    except Exception as e:
                        driver.switch_to.default_content()
                        continue
                else:
                    # No suitable iframe found, stay in main content
                    driver.switch_to.default_content()
            except Exception as e:
                pass

            # Try multiple selectors for the postcode input
            postcode_input = None
            selectors = [
                '[aria-label="Enter your address"]',
                'input[placeholder*="postcode"]',
                'input[placeholder*="address"]',
                'input[type="text"]'
            ]
            
            for selector in selectors:
                try:
                    postcode_input = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not postcode_input:
                raise ValueError("Could not find postcode input field")

            postcode_input.send_keys(user_postcode)

            find_address_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "submitButton0"))
            )
            find_address_button.click()

            time.sleep(15)
            # Wait for address box to be visible
            select_address_input = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        '[aria-label="Select full address"]',
                    )
                )
            )

            # Select address based
            select = Select(select_address_input)
            # Grab the first option as a template
            first_option = select.options[0].accessible_name
            template_parts = first_option.split(", ")
            template_parts[0] = user_paon  # Replace the first part with user_paon

            addr_label = ", ".join(template_parts)
            for addr_option in select.options:
                option_name = addr_option.accessible_name[0 : len(addr_label)]
                if option_name == addr_label:
                    break
            select.select_by_value(addr_option.text)

            time.sleep(10)
            # Wait for the specified div to be present
            target_div_id = "FinalResults"
            target_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, target_div_id))
            )

            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # Find the div with the specified id
            target_div = soup.find("div", {"id": target_div_id})

            # Check if the div is found
            if target_div:
                bin_data = {"bins": []}

                for bin_div in target_div.find_all("div"):
                    # Extract the collection date from the message
                    try:
                        bin_collection_message = bin_div.find("p").text.strip()
                        date_pattern = r"\b\d{2}/\d{2}/\d{4}\b"

                        collection_date_string = (
                            re.search(date_pattern, bin_div.text)
                            .group(0)
                            .strip()
                            .replace(",", "")
                        )
                    except AttributeError:
                        continue

                    current_date = datetime.now()
                    parsed_date = datetime.strptime(collection_date_string, "%d/%m/%Y")
                    # Check if the parsed date is in the past and not today
                    if parsed_date.date() < current_date.date():
                        # If so, set the year to the next year
                        parsed_date = parsed_date.replace(year=current_date.year + 1)
                    else:
                        # If not, set the year to the current year
                        parsed_date = parsed_date.replace(year=current_date.year)
                    formatted_date = parsed_date.strftime("%d/%m/%Y")
                    contains_date(formatted_date)

                    # Extract the bin type from the message
                    bin_type_match = re.search(
                        r"Your next (.*?) collection", bin_collection_message
                    )
                    if bin_type_match:
                        bin_info = {
                            "type": bin_type_match.group(1),
                            "collectionDate": formatted_date,
                        }
                        bin_data["bins"].append(bin_info)
            else:
                raise ValueError("Collection data not found.")

        except Exception as e:
            # Here you can log the exception if needed
            print(f"An error occurred: {e}")
            # Optionally, re-raise the exception if you want it to propagate
            raise
        finally:
            # This block ensures that the driver is closed regardless of an exception
            if driver:
                driver.quit()
        return bin_data
