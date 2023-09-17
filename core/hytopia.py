from random import choice

from fake_useragent import UserAgent  # pip install fake-useragent

from core.utils import str_to_file, logger, CaptchaService
from string import ascii_lowercase, digits
from aiohttp import ClientSession

from core.utils import Person
from inputs.config import (
    MOBILE_PROXY,
    MOBILE_PROXY_CHANGE_IP_LINK
)


class Hytopia(ClientSession, Person):
    referral = None

    def __init__(self, email: str):
        headers = {
            'authority': 'preregister.hytopia.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'origin': 'https://preregister.hytopia.com',
            'referer': 'https://preregister.hytopia.com/sasha06660/',
            'user-agent': UserAgent().random,
        }

        ClientSession.__init__(self, headers=headers, trust_env=True)
        Person.__init__(self)

        self.email = email

        self.proxy = None

    async def define_proxy(self, proxy: str):
        if MOBILE_PROXY:
            await Hytopia.change_ip()
            self.proxy = MOBILE_PROXY

        if proxy is not None:
            self.proxy = f"http://{proxy}"

    @staticmethod
    async def change_ip():
        async with ClientSession() as session:
            await session.get(MOBILE_PROXY_CHANGE_IP_LINK)

    async def enter_beta(self):
        url = f'https://preregister.hytopia.com/{Hytopia.referral}/'

        params = {
            '_data': 'player-by-referrer',
        }

        data = {
            'username': self.username,
            'email': self.email,
            'g-recaptcha-response': await Hytopia.bypass_captcha(),
        }

        async with self.post(url, params=params, data=data, proxy=self.proxy, ssl=False) as resp:
            return await resp.json()

    @staticmethod
    async def bypass_captcha():
        captcha_service = CaptchaService()
        return await captcha_service.get_captcha_token()

    def logs(self, file_name: str, msg_result: str = ""):
        file_msg = f"{self.email}|{self.username}|{self.proxy}"
        str_to_file(f"./logs/{file_name}.txt", file_msg)
        msg_result = msg_result and " | " + str(msg_result)

        if file_name == "success":
            logger.success(f"{self.email}{msg_result}")
        else:
            logger.error(f"{self.email}{msg_result}")

    @staticmethod
    def generate_password(k=10):
        return ''.join([choice(ascii_lowercase + digits) for _ in range(k)])
