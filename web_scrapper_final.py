# import re
# import requests
# import pandas as pd  # For reading CSV/Excel files
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from bs4 import BeautifulSoup
# import time
# import random
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from fake_useragent import UserAgent
# import logging
# from selenium.common.exceptions import WebDriverException, TimeoutException

# # Setup logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# def initialize_webdriver():
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--enable-unsafe-swiftshader")

#     ua = UserAgent()
#     user_agent = ua.random
#     chrome_options.add_argument(f"user-agent={user_agent}")

#     try:
#         # Try to use the default ChromeDriver
#         driver = webdriver.Chrome(options=chrome_options)
#     except WebDriverException:
#         try:
#             # If default fails, try to use the specified path
#             service = Service('C:/Users/RONAK/Downloads/chrome-win64/chrome-win64/chrome.exe')
#             driver = webdriver.Chrome(service=service, options=chrome_options)
#         except WebDriverException as e:
#             logger.error(f"Failed to initialize WebDriver: {str(e)}")
#             logger.info("Please ensure ChromeDriver is installed and the path is correct.")
#             return None

#     return driver

# def get_product_name_and_asin(url, max_retries=3):
#     for attempt in range(max_retries):
#         asin_match = re.search(r'/([A-Z0-9]{10})(?:[/?]|$)', url)
#         asin = asin_match.group(1) if asin_match else "ASIN not found in URL"

#         driver = initialize_webdriver()
#         if not driver:
#             logger.error(f"Failed to initialize WebDriver for product name and ASIN, attempt {attempt + 1} of {max_retries}")
#             if attempt == max_retries - 1:
#                 return "Failed to initialize WebDriver", asin
#             continue

#         try:
#             driver.get(url)
#             WebDriverWait(driver, 20).until(EC.title_contains("Amazon"))  # Increased timeout
#             soup = BeautifulSoup(driver.page_source, 'html.parser')

#             title_tag = soup.find('title')
#             product_name = title_tag.get_text(strip=True) if title_tag else "Product name not found"

#             return product_name, asin
#         except Exception as e:
#             logger.error(f"Error in get_product_name_and_asin (attempt {attempt + 1}): {str(e)}")
#             if attempt == max_retries - 1:
#                 return "Error occurred while fetching product details", asin
#         finally:
#             driver.quit()

#         # Wait before retry
#         if attempt < max_retries - 1:
#             time.sleep(random.randint(5, 10))

# def get_variants(url, max_retries=3):
#     for attempt in range(max_retries):
#         driver = initialize_webdriver()
#         if not driver:
#             logger.error(f"Failed to initialize WebDriver for variants, attempt {attempt + 1} of {max_retries}")
#             if attempt == max_retries - 1:
#                 return []
#             continue

#         variants = []

#         try:
#             # Open the main product page
#             driver.get(url)
#             WebDriverWait(driver, 60).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, 'span.a-button-thumbnail, li[id^="color_name_"]'))
#             )

#             # Extract initial size and color variants
#             soup = BeautifulSoup(driver.page_source, 'html.parser')

#             size_variants = []
#             color_variants = []

#             # Extract size variants
#             size_elements = soup.find_all('li', id=lambda x: x and x.startswith('size_name_'))
#             for size_element in size_elements:
#                 size_name = size_element.get('title', '').replace('Click to select ', '')
#                 size_asin = size_element.get('data-defaultasin', '')
#                 if size_name:
#                     size_variants.append((size_name, size_asin))

#             # Check if there are any size or color variants
#             if not size_variants:
#                 color_elements = soup.find_all('li', id=lambda x: x and x.startswith('color_name_'))
#                 if not color_elements:
#                     return None  # Return None if no variants found

#             # Iterate over size variants to extract corresponding color variants
#             for size_name, size_asin in size_variants:
#                 # Construct URL for each size variant
#                 if size_asin:
#                     size_url = re.sub(r'/([A-Z0-9]{10})(?:[/?]|$)', f'/{size_asin}/', url)
#                 else:
#                     size_url = url

#                 # Navigate to size variant page with retry mechanism
#                 retry_success = False
#                 for retry in range(3):
#                     try:
#                         driver.get(size_url)
#                         WebDriverWait(driver, 60).until(
#                             EC.presence_of_element_located((By.CSS_SELECTOR, 'li[id^="color_name_"]'))
#                         )
#                         retry_success = True
#                         break
#                     except TimeoutException as e:
#                         logger.warning(f"Retry {retry + 1}: Failed to load size variant page - {str(e)}")
#                         time.sleep(random.randint(5, 10))

#                 if not retry_success:
#                     continue

#                 time.sleep(5)  # Allow time for the page to load fully

#                 # Extract color variants for this size
#                 soup = BeautifulSoup(driver.page_source, 'html.parser')
#                 color_elements = soup.find_all('li', id=lambda x: x and x.startswith('color_name_'))
#                 for color_element in color_elements:
#                     color_name = color_element.get('title', '').replace('Click to select ', '')
#                     color_asin = color_element.get('data-defaultasin', '')
#                     if color_name:
#                         variants.append((f"Size: {size_name}, Color: {color_name}", color_asin))

#             # Fallback for color-only variants
#             if not size_variants:
#                 color_elements = soup.find_all('li', id=lambda x: x and x.startswith('color_name_'))
#                 for color_element in color_elements:
#                     color_name = color_element.get('title', '').replace('Click to select ', '')
#                     color_asin = color_element.get('data-defaultasin', '')
#                     if color_name:
#                         variants.append((f"Color: {color_name}", color_asin))

#             return variants

#         except Exception as e:
#             logger.error(f"Error in get_variants (attempt {attempt + 1}): {str(e)}")
#             if attempt == max_retries - 1:
#                 return []
#         finally:
#             driver.quit()

#         # Wait before retry
#         if attempt < max_retries - 1:
#             time.sleep(random.randint(5, 10))

# def process_urls_from_file(file_path):
#     try:
#         # Read the CSV or Excel file
#         if file_path.endswith('.csv'):
#             data = pd.read_csv(file_path)
#         elif file_path.endswith('.xlsx'):
#             data = pd.read_excel(file_path)
#         else:
#             logger.error("Unsupported file format. Please use a CSV or Excel file.")
#             return

#         # Ensure the file has a 'URL' column
#         if 'URL' not in data.columns:
#             logger.error("The file must contain a 'URL' column.")
#             return

#         # Process each URL
#         results = []
#         total_urls = len(data['URL'])
#         for index, url in enumerate(data['URL'], 1):
#             logger.info(f"Processing URL {index} of {total_urls}: {url}")

#             # Get product details
#             product_name, asin = get_product_name_and_asin(url)
#             variants = get_variants(url)

#             if variants is None:
#                 variants_info = "No variants found"
#             else:
#                 variants_info = "; ".join([f"{variant_name} (ASIN: {variant_asin})" for variant_name, variant_asin in variants])

#             results.append({
#                 "URL": url,
#                 "Product Name": product_name,
#                 "ASIN": asin,
#                 "Variants": variants_info
#             })

#             # Save intermediate results
#             pd.DataFrame(results).to_csv("D:/am1/scraped_results_intermediate.csv", index=False)

#             # Random delay between URLs
#             if index < total_urls:
#                 delay = random.randint(30, 60)
#                 logger.info(f"Waiting {delay} seconds before processing the next URL...")
#                 time.sleep(delay)

#         # Save final results
#         output_file = "D:/am1/scraped_results.csv"
#         pd.DataFrame(results).to_csv(output_file, index=False)
#         logger.info(f"Scraping completed. Results saved to {output_file}")

#     except Exception as e:
#         logger.error(f"An error occurred while processing the file: {str(e)}")

# # Main execution
# file_path = "C:/Users/RONAK/Downloads/Book1.csv"  # Replace with the path to your CSV/Excel file
# process_urls_from_file(file_path)



import re
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import logging
from selenium.common.exceptions import WebDriverException, TimeoutException

# Setup logging with more detailed configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('amazon_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def initialize_webdriver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--enable-unsafe-swiftshader")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--enable-javascript")

    ua = UserAgent()
    user_agent = ua.random
    chrome_options.add_argument(f"user-agent={user_agent}")

    try:
        driver = webdriver.Chrome(options=chrome_options)
    except WebDriverException:
        try:
            service = Service('C:/Users/RONAK/Downloads/chrome-win64/chrome-win64/chrome.exe')
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except WebDriverException as e:
            logger.error(f"Failed to initialize WebDriver: {str(e)}")
            return None

    return driver

def wait_for_variants(driver):
    try:
        # Wait for initial variant elements
        WebDriverWait(driver, 90).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span.a-button-thumbnail, li[id^="color_name_"], li[id^="size_name_"]'))
        )
        
        # Wait for dynamic content to load
        time.sleep(5)  # Short wait for dynamic content
        
        # Scroll to ensure all variants are loaded
        driver.execute_script("""
            var elements = document.querySelectorAll('span.a-button-thumbnail, li[id^="color_name_"], li[id^="size_name_"]');
            elements[elements.length-1].scrollIntoView();
        """)
        
        time.sleep(3)  # Wait after scroll
        
    except TimeoutException as e:
        logger.warning(f"Timeout waiting for variants: {str(e)}")
        return False
    return True

def extract_asin(element):
    """Enhanced ASIN extraction with multiple fallback methods"""
    possible_asin_sources = [
        lambda e: e.get('data-defaultasin'),
        lambda e: e.get('data-asin'),
        lambda e: re.search(r'/([A-Z0-9]{10})(?:[/?]|$)', e.get('data-dp-url', '')).group(1) if e.get('data-dp-url') else None,
        lambda e: re.search(r'/([A-Z0-9]{10})(?:[/?]|$)', e.find('a')['href']).group(1) if e.find('a', href=True) else None
    ]
    
    for source in possible_asin_sources:
        try:
            asin = source(element)
            if asin and re.match(r'^[A-Z0-9]{10}$', asin):
                return asin
        except (AttributeError, KeyError, IndexError):
            continue
    
    return ''

def get_product_name_and_asin(url, max_retries=3):
    for attempt in range(max_retries):
        asin_match = re.search(r'/([A-Z0-9]{10})(?:[/?]|$)', url)
        asin = asin_match.group(1) if asin_match else "ASIN not found in URL"

        driver = initialize_webdriver()
        if not driver:
            logger.error(f"Failed to initialize WebDriver, attempt {attempt + 1}")
            continue

        try:
            driver.get(url)
            WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.TAG_NAME, "title")))
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            title_element = soup.find('span', {'id': 'productTitle'}) or soup.find('title')
            product_name = title_element.get_text(strip=True) if title_element else "Product name not found"

            return product_name, asin

        except Exception as e:
            logger.error(f"Error in get_product_name_and_asin (attempt {attempt + 1}): {str(e)}")
            if attempt == max_retries - 1:
                return "Error occurred while fetching product details", asin
        finally:
            driver.quit()

        time.sleep(random.randint(10, 15))

def get_variants(url, max_retries=3):
    for attempt in range(max_retries):
        driver = initialize_webdriver()
        if not driver:
            continue

        variants = []
        try:
            driver.get(url)
            if not wait_for_variants(driver):
                continue

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extract size variants
            size_variants = []
            size_elements = soup.find_all('li', id=lambda x: x and x.startswith('size_name_'))
            
            for size_element in size_elements:
                size_name = size_element.get('title', '').replace('Click to select ', '')
                size_asin = extract_asin(size_element)
                if size_name and size_asin:
                    size_variants.append((size_name, size_asin))
                    logger.debug(f"Found size variant: {size_name} with ASIN: {size_asin}")

            # Handle products with both size and color variants
            if size_variants:
                for size_name, size_asin in size_variants:
                    variant_url = re.sub(r'/([A-Z0-9]{10})(?:[/?]|$)', f'/{size_asin}/', url)
                    
                    try:
                        driver.get(variant_url)
                        wait_for_variants(driver)
                        
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                        color_elements = soup.find_all('li', id=lambda x: x and x.startswith('color_name_'))
                        
                        if color_elements:
                            for color_element in color_elements:
                                color_name = color_element.get('title', '').replace('Click to select ', '')
                                color_asin = extract_asin(color_element)
                                if color_name and color_asin:
                                    variants.append((f"Size: {size_name}, Color: {color_name}", color_asin))
                                    logger.debug(f"Found color variant for size {size_name}: {color_name} with ASIN: {color_asin}")
                        else:
                            # If no color variants, add size variant alone
                            variants.append((f"Size: {size_name}", size_asin))
                            
                    except Exception as e:
                        logger.error(f"Error processing variant URL: {str(e)}")
                        continue
            else:
                # Handle color-only variants
                color_elements = soup.find_all('li', id=lambda x: x and x.startswith('color_name_'))
                for color_element in color_elements:
                    color_name = color_element.get('title', '').replace('Click to select ', '')
                    color_asin = extract_asin(color_element)
                    if color_name and color_asin:
                        variants.append((f"Color: {color_name}", color_asin))
                        logger.debug(f"Found color variant: {color_name} with ASIN: {color_asin}")

            return variants if variants else None

        except Exception as e:
            logger.error(f"Error in get_variants (attempt {attempt + 1}): {str(e)}")
            if attempt == max_retries - 1:
                return None
        finally:
            driver.quit()

        time.sleep(random.randint(10, 15))

def process_urls_from_file(file_path):
    try:
        # Read the input file
        if file_path.endswith('.csv'):
            data = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            data = pd.read_excel(file_path)
        else:
            logger.error("Unsupported file format. Please use CSV or Excel file.")
            return

        if 'URL' not in data.columns:
            logger.error("The file must contain a 'URL' column.")
            return

        results = []
        total_urls = len(data['URL'])
        
        for index, url in enumerate(data['URL'], 1):
            logger.info(f"Processing URL {index}/{total_urls}: {url}")
            
            product_name, asin = get_product_name_and_asin(url)
            variants = get_variants(url)

            if variants is None:
                results.append({
                    "URL": url,
                    "Product Name": product_name,
                    "ASIN": asin,
                    "Variant": "No variants found"
                })
                logger.info(f"No variants found for {url}")
            else:
                for variant_name, variant_asin in variants:
                    results.append({
                        "URL": url,
                        "Product Name": product_name,
                        "ASIN": asin,
                        "Variant": f"{variant_name} (ASIN: {variant_asin})"
                    })
                logger.info(f"Found {len(variants)} variants for {url}")

        # Save results
        output_file = "D:/amazon web scrapper/scraped_results.csv"
        pd.DataFrame(results).to_csv(output_file, index=False)
        logger.info(f"Scraping completed. Results saved to {output_file}")

    except Exception as e:
        logger.error(f"An error occurred while processing the file: {str(e)}")

if __name__ == "__main__":
    file_path = "D:/amazon web scrapper/Book1.csv"  # Update this path to your input file
    process_urls_from_file(file_path)

#.............this is the final code for now......getting all varients and names properly...............