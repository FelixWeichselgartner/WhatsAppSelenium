import platform
import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import logging
from selenium.webdriver.remote.remote_connection import LOGGER
logging.basicConfig(level=logging.INFO)

from tqdm import tqdm
from time import sleep


XPATH_search_bar = """/html/body/div[1]/div/div/div/div/div[3]/div/div[4]/div/div[1]/div/div[2]/div/div/div[1]"""
XPATH_chat_box   = """/html/body/div[1]/div/div/div/div/div[3]/div/div[5]/div/footer/div[1]/div/span/div/div[2]/div/div[3]/div[1]"""
XPATH_contact    = """/html/body/div[1]/div/div/div/div/div[3]/div/div[4]/div/div[3]/div[1]/div/div/div"""


def find_elements_by_text(driver, tag_name, text, timeout=10):
    """
    Searches for elements by their text content.
    """
    try:
        xpath = f"//{tag_name}[contains(text(), '{text}')]"
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return driver.find_elements(By.XPATH, xpath)
    except Exception as e:
        print(f"Error finding elements with text '{text}': {e}")
        return []


def find_elements_by_text_with_xpath(driver, tag_name, text, timeout=10):
    """
    Searches for elements by their text content and returns the elements with their XPath.
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

        result = []
        for element in elements:
            calculated_xpath = get_xpath(element)
            result.append((element, calculated_xpath))

        return result
    except Exception as e:
        print(f"Error finding elements with text '{text}': {e}")
        return []


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
        try:
            self.driver = webdriver.Firefox(service=service, options=options)
        except WebDriverException as e:
            LOGGER.error(e)
            LOGGER.error('Did you start from vscode? Try to start from Terminal.')
            exit(127)

        self.driver.get('https://web.whatsapp.com/')
        self.wait_login()

    def __del__(self):
        """
        close the web browser.
        """
        sleep(1)
        print('closing whatsapp')

        if hasattr(self, "driver") and self.driver is not None:
            self.driver.quit()
            self.driver = None

    def search_bar(self):
        """
        find the search bar for searching contacts.
        :return: the search bar.
        """
        try:
            ret = self.driver.find_element(By.XPATH, XPATH_search_bar)
        except selenium.common.exceptions.NoSuchElementException:
            ret = None
        return ret

    def wait_login(self, timeout=120):
        """
        wait until logged in whatsapp web session.
        """
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, XPATH_search_bar))
        )
        print('logged-in in WhatsApp')

    def chat_box(self):
        """
        find the chat box.
        :return: the chat box.
        """
        try:
            ret = self.driver.find_element(By.XPATH, XPATH_chat_box)
        except selenium.common.exceptions.NoSuchElementException:
            ret = None
        return ret

    def wait_for_clickable(self, xpath, timeout=20):
        """
        Wait for an element located by XPath to be clickable, retrying on stale references.
        """
        locator = (By.XPATH, xpath)
        wait = WebDriverWait(
            self.driver,
            timeout,
            ignored_exceptions=(StaleElementReferenceException,)
        )

        def _predicate(driver):
            try:
                elem = driver.find_element(*locator)
                if elem.is_displayed() and elem.is_enabled():
                    return elem
                return False
            except StaleElementReferenceException:
                return False

        return wait.until(_predicate)

    def contact_available(self):
        """
        Check if contact is available and click it.
        """
        sleep(5)

        # Get all matching contact elements instead of trying div[0], div[1], ...
        try:
            elements = self.driver.find_elements(By.XPATH, XPATH_contact)
        except selenium.common.exceptions.NoSuchElementException:
            return False

        for i, obj in enumerate(elements, start=1):
            print(f'Try {i}')
            print(f"{XPATH_contact}[{i}] (logical index)")
            try:
                style = obj.get_attribute('style')
            except StaleElementReferenceException:
                continue

            if style and 'transform: translateY(76px)' in style:
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

            # Wait for search bar explicitly
            sb = WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, XPATH_search_bar))
            )
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

            # --- stale-safe wait for chat box ---
            cb = self.wait_for_clickable(XPATH_chat_box, timeout=20)
            cb.click()

            tqdm.write(steps[5])
            pbar.update(1)

            sleep(1)

            # Re-acquire in case WhatsApp changed the DOM again
            cb = self.wait_for_clickable(XPATH_chat_box, timeout=20)

            tqdm.write(steps[6])
            pbar.update(1)

            lines = [line for line in message.split('\n') if line]
            for line in lines:
                for attempt in range(3):
                    try:
                        for c in line:
                            cb.send_keys(c)
                        action.key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()
                        break
                    except StaleElementReferenceException:
                        cb = self.wait_for_clickable(XPATH_chat_box, timeout=20)
                else:
                    raise RuntimeError("Chat box kept going stale while typing message.")

            cb.send_keys(Keys.RETURN)
            sleep(0.5)
            tqdm.write(steps[7])
            pbar.update(1)

            return True
