import random
from asyncio import Semaphore, create_task, gather, sleep

from core.utils import file_to_list, shift_file, logger
from core.hytopia import Hytopia
from core.utils.auto_generate import generate_random_emails

from inputs.config import (
    REFERRAL, THREADS, CUSTOM_DELAY, EMAILS_FILE_PATH, PROXIES_FILE_PATH
)


class AutoReger:
    def __init__(self):
        self.success = 0

    @staticmethod
    def get_accounts():
        emails = file_to_list(EMAILS_FILE_PATH)
        proxies = file_to_list(PROXIES_FILE_PATH)

        if not emails:
            logger.info(f"Generated random emails!")
            emails = generate_random_emails(100)

        min_accounts_len = len(emails)

        accounts = []

        for i in range(min_accounts_len):
            accounts.append((*emails[i].split(":")[:1], proxies[i] if len(proxies) > i else None))

        return accounts

    @staticmethod
    def remove_account():
        return shift_file(EMAILS_FILE_PATH), shift_file(PROXIES_FILE_PATH)

    async def start(self):
        Hytopia.referral = REFERRAL.split('/')[-1]

        accounts = AutoReger.get_accounts()

        logger.info(f"Successfully grab {len(accounts)} accounts")

        semaphore = Semaphore(THREADS)

        tasks = []
        for account in accounts:
            task = create_task(self.register(account, semaphore))
            tasks.append(task)

        await gather(* tasks)

        if self.success:
            logger.success(f"Successfully registered {self.success} accounts :)")
        else:
            logger.warning(f"No accounts registered :(")

    async def register(self, account: tuple, semaphore: Semaphore):
        email, proxy = account
        logs = {"ok": False, "msg": ""}

        try:
            async with semaphore:
                async with Hytopia(email) as hytopia:
                    await AutoReger.custom_delay()

                    await hytopia.define_proxy(proxy)

                    resp_json = await hytopia.enter_beta()

                logger.debug(resp_json)
                success = resp_json.get("success")

                logs["ok"] = success
                if not logs["ok"]:
                    logs["msg"] = resp_json.get("error", resp_json)
        except Exception as e:
            logs["msg"] = e
            logger.error(f"Error {e}")

        AutoReger.remove_account()

        if logs["ok"]:
            hytopia.logs("success", logs["msg"])
            self.success += 1
        else:
            hytopia.logs("fail", logs["msg"])

    @staticmethod
    async def custom_delay():
        if CUSTOM_DELAY[1] > 0:
            sleep_time = random.uniform(CUSTOM_DELAY[0], CUSTOM_DELAY[1])
            logger.info(f"Sleep for {int(sleep_time)} seconds")
            await sleep(sleep_time)

    @staticmethod
    def is_file_empty(path: str):
        return not open(path).read().strip()
