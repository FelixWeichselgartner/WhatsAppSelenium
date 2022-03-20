# WhatsApp Selenium

Use Python to send automated WhatsApp messages over Firefox with Selenium.


## Disclaimer

I'm not affiliated or authorized by Meta/Facebook/WhatsApp. Use this at your own risk. I'm not responsible for failed/wrong send messages. Sometimes WhatsApp changes some xpath, so make sure to test every single time, before using this for an application, that mustn't fail. If there is an error, it's mostly some changed xpath, sometimes a geckodriver update is required.


## Usage

Setup:
* [Download](https://github.com/mozilla/geckodriver/releases) geckodriver for your platform.
* Unpack geckodriver in this directory.
* Locate your profile path with firefox (this saves your WhatsApp Web session).
    * Three-bars (top right corner) in Firefox
    * Help 
    * More troubleshooting information
    * Copy the `Profile Directory` as your profile path
* Have the WhatsApp numbers as contacts saved on your phone.
* Sign in with WhatsApp Web.
* Create a WhatsApp object.
* Use WhatsApp.send_message to send your messages.


## License

GNU General Public License Version 3, see [License](./License.md)
