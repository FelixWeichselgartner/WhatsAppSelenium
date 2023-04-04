import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

import logging
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.WARNING)

from time import sleep


class WhatsApp:
    """
    class for sending whatsapp messages via whatsapp web.
    """

    def __init__(self, firefox_path, gecko_path):
        """
        determine firefox path:
        - open firefox
        - right upper corner "three -"
        - help
        - Troubleshooting information
        - Profile directory
        """

        self._profile_path = firefox_path
        self._LOCAL_STORAGE_FILE = 'localStorage.json'
        self.options = Options()
        self._profile = webdriver.FirefoxProfile(profile_directory=self._profile_path)
        self.options.profile = self._profile
        self.web = webdriver.Firefox(executable_path=gecko_path, options=self.options)
        # self.web.minimize_window()
        self.web.get('https://web.whatsapp.com/')
        self.wait_login()

    def __del__(self):
        """
        close the web browser.
        :return:
        """

        sleep(10)

        print('closing whatsapp')

        if 'web' in self.__dict__ and self.web != None:
            self.web.quit()
            self.web = None
        else:
            print('##################################')

    def search_bar(self):
        """
        find the search bar for searching contacts.
        :return: the search bar.
        """

        try:          
                                                    
            ret = self.web.find_element("xpath", """/html/body/div[1]/div/div/div[4]/div/div[1]/div/div/div[2]/div/div[1]""")
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
            ret = self.web.find_element("xpath", """/html/body/div[1]/div/div/div[5]/div/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]""")          
            #ret = self.web.find_element_by_xpath("""/html/body/div[1]/div[1]/div[1]/div[4]/div[1]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[2]""")                                                    
        except selenium.common.exceptions.NoSuchElementException:
            ret = None
        return ret

    def contact_available(self):
        sleep(5)

        for i in range(15):
            try:
                obj = self.web.find_element("xpath", f"/html/body/div[1]/div/div/div[4]/div/div[2]/div[1]/div/div/div[{i}]")
            except selenium.common.exceptions.NoSuchElementException:
                continue
            if 'transform: translateY(72px)' in obj.get_attribute('style'):
                obj.click()
                return True
        return False

    def send_message(self, phone_number, message) -> bool:
        """
        send message "message" to "phone_number"
        :param phone_number: the phone number to send the message to.
        :param message: the message to send.
        :return: True if message send,
                 False if not send.
        """

        action = ActionChains(self.web)

        while True:
            sb = self.search_bar()
            if sb is not None:
                break
        try:
            sb.clear()
            for i in range(50):
                action.send_keys(Keys.BACK_SPACE).perform()
        except selenium.common.exceptions.ElementNotInteractableException:
            pass

        for pn in phone_number:
            sb.send_keys(pn)
        #sb.send_keys(phone_number)
        sleep(2)

        if self.contact_available():
            sb.send_keys('\n')
            logging.info(f'sending message to {phone_number}')
        else:
            return False

        while True:
            cb = self.chat_box()
            if cb is not None:
                break
        l = list(filter(lambda x: x != '', message.split('\n')))
        
        
        cb.click()
        for line in l:
            for c in line:
                cb.send_keys(c)
            action.key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()
        cb.send_keys('\n')
        cb.send_keys(Keys.RETURN)

        sleep(0.5)
        return True
