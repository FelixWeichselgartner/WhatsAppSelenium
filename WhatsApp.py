import platform
import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import logging
from selenium.webdriver.remote.remote_connection import LOGGER
logging.basicConfig(level=logging.INFO)

from tqdm import tqdm
from time import sleep

                      
XPATH_search_bar = """/html/body/div[1]/div/div/div[3]/div/div[3]/div/div[1]/div/div[2]/div/div/div"""      
XPATH_chat_box   = """/html/body/div[1]/div/div/div[3]/div/div[4]/div/footer/div[1]/div/span/div/div[2]/div/div[3]/div[1]"""
XPATH_contact    = """/html/body/div[1]/div/div/div[3]/div/div[3]/div/div[3]/div[1]/div/div/div"""    


def find_elements_by_text(driver, tag_name, text, timeout=10):
    """
    Searches for elements by their text content.

    Parameters:
    - driver: Selenium WebDriver instance.
    - tag_name: HTML tag to search for (e.g., 'div', 'p').
    - text: The exact text to match within the element.
    - timeout: Maximum time to wait for the element to appear (default is 10 seconds).

    Returns:
    - A list of matching WebElement objects, or an empty list if none are found.
    """
    try:
        xpath = f"//{tag_name}[contains(text(), '{text}')]"
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return driver.find_elements(By.XPATH, xpath)
    except Exception as e:
        print(f"Error finding elements with text '{text}': {e}")
        return []

"""# Example Usage
# Assuming `driver` is your Selenium WebDriver instance
# Example for "Suchen" button
suchen_elements = find_elements_by_text(driver, "div", "Suchen")

# Example for "Gib eine Nachricht ein."
message_box_elements = find_elements_by_text(driver, "div", "Gib eine Nachricht ein.")

# If you expect only one element, you can access it like:
if message_box_elements:
    message_box = message_box_elements[0]
    print("Found message box:", message_box.text)"""


def find_elements_by_text_with_xpath(driver, tag_name, text, timeout=10):
    """
    Searches for elements by their text content and returns the elements with their XPath.

    Parameters:
    - driver: Selenium WebDriver instance.
    - tag_name: HTML tag to search for (e.g., 'div', 'p').
    - text: The exact text to match within the element.
    - timeout: Maximum time to wait for the element to appear (default is 10 seconds).

    Returns:
    - A list of tuples, each containing the WebElement and its calculated XPath.
    """
    def get_xpath(element):
        """
        Generates the XPath for a WebElement by traversing up the DOM tree.
        """
        components = []
        child = element
        while child is not None:
            parent = child.find_element(By.XPATH, "..")
            siblings = parent.find_elements(By.XPATH, f"./{child.tag_name}")
            index = siblings.index(child) + 1
            components.append(f"{child.tag_name}[{index}]")
            child = parent if parent.tag_name != "html" else None
        components.reverse()
        return "/" + "/".join(components)

    try:
        xpath = f"//{tag_name}[contains(text(), '{text}')]"
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
        elements = driver.find_elements(By.XPATH, xpath)

        # Generate XPath for each found element
        result = []
        for element in elements:
            calculated_xpath = get_xpath(element)
            result.append((element, calculated_xpath))
        
        return result
    except Exception as e:
        print(f"Error finding elements with text '{text}': {e}")
        return []
"""
# Example Usage
# Assuming `driver` is your Selenium WebDriver instance
found_elements = find_elements_by_text_with_xpath(driver, "div", "Suchen")

for element, xpath in found_elements:
    print("Element Text:", element.text)
    print("Generated XPath:", xpath)"""



class WhatsApp:
    """
    class for sending whatsapp messages via whatsapp web.
    """

    def __init__(self, firefox_path):
        """
        determine firefox path:
        - open firefox
        - right upper corner "three -"
        - help
        - Troubleshooting information
        - Profile directory
        """

        options = Options()
        if platform.system() == 'Windows':
            options.binary_location = r"C:/Program Files/Mozilla Firefox/firefox.exe"
        elif platform.system() == 'Linux':
            options.binary_location = "/usr/lib64/firefox/firefox"
        else:
            print('Your system is not supported by WhatsAppSelenium')
        print(firefox_path)
        options.profile = webdriver.FirefoxProfile(profile_directory=firefox_path)

        # Setup the driver with automatic geckodriver management
        service = Service(executable_path=GeckoDriverManager().install())
        #service = Service(executable_path=gecko_path)
        try:
            self.driver = webdriver.Firefox(service=service, options=options)
        except WebDriverException as e:
            LOGGER.error(e)
            LOGGER.error('Did you start from vscode? Try to start from Terminal.')
            exit(127)
        # self.driver.minimize_window()
        self.driver.get('https://web.whatsapp.com/')
        self.wait_login()

    def __del__(self):
        """
        close the web browser.
        :return:
        """

        sleep(1)

        print('closing whatsapp')

        if 'web' in self.__dict__ and self.driver != None:
            self.driver.quit()
            self.driver = None

    def search_bar(self):
        """
        find the search bar for searching contacts.
        :return: the search bar.
        """

        try:
            ret = self.driver.find_element("xpath", XPATH_search_bar)
        except selenium.common.exceptions.NoSuchElementException:
            ret = None
        return ret

    def wait_login(self):
        """
        wait until logged in whatsapp web session.
        :return:
        """

        while not self.search_bar():
            pass
        print('logged-in in WhatsApp')

    def chat_box(self):
        """
        find the chat box.
        :return: the chat box.
        """

        # <div class="wjdTm" style="visibility: visible;">Schreib eine Nachricht</div>
        # xpath:
        try:
            ret = self.driver.find_element("xpath", XPATH_chat_box)
        except selenium.common.exceptions.NoSuchElementException:
            ret = None
        return ret

    def contact_available(self):
        sleep(5)

        for i in range(15):
            try:
                obj = self.driver.find_element("xpath", XPATH_contact + f"[{i}]")
            except selenium.common.exceptions.NoSuchElementException:
                continue
            if 'transform: translateY(76px)' in obj.get_attribute('style'):
                obj.click()
                return True
        return False

    def send_message(self, phone_number, message) -> bool:
        """
        Send a message to a phone number using WhatsApp Web.
        """

        steps = [
            f"Start sending message for {phone_number}",
            "Waiting for search bar",
            "Clearing search bar",
            "Entering phone number",
            "Checking contact availability",
            "Waiting for chat box",
            "Typing message",
            "Sending message - done ✅"
        ]

        with tqdm(total=len(steps), bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
            tqdm.write(steps[0])
            pbar.update(1)

            action = ActionChains(self.driver)

            while True:
                sb = self.search_bar()
                if sb is not None:
                    break
            tqdm.write(steps[1])
            pbar.update(1)
            sb.click()

            try:
                sb.clear()
                for _ in range(50):
                    action.send_keys(Keys.BACK_SPACE).perform()
            except selenium.common.exceptions.ElementNotInteractableException:
                pass
            tqdm.write(steps[2])
            pbar.update(1)

            for pn in phone_number:
                sb.send_keys(pn)
            sleep(2)
            tqdm.write(steps[3])
            pbar.update(1)

            if self.contact_available():
                sb.send_keys('\n')
                tqdm.write(f"sending message to {phone_number}")
            else:
                tqdm.write(f"Contact not found for {phone_number} – skipping")
                return False
            pbar.update(1)

            while True:
                cb = self.chat_box()
                if cb is not None:
                    break
            tqdm.write(steps[5])
            pbar.update(1)

            l = list(filter(lambda x: x != '', message.split('\n')))
            cb.click()
            for line in l:
                for c in line:
                    cb.send_keys(c)
                action.key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()
            tqdm.write(steps[6])
            pbar.update(1)

            cb.send_keys('\n')
            cb.send_keys(Keys.RETURN)
            sleep(0.5)
            tqdm.write(steps[7])
            pbar.update(1)

            return True

