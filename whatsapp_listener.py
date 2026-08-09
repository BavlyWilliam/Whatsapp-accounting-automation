from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
import time
import os
import re
from datetime import datetime

from main import process_message
from Sheets_connector import get_sheet
from config_loader import load_config
from logger import setup_logger


def start_browser(profile_folder):
    profile_path = os.path.abspath(profile_folder)
    os.makedirs(profile_path, exist_ok=True)

    lock_file = os.path.join(profile_path, "lock")
    if os.path.exists(lock_file):
        os.remove(lock_file)

    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument("-profile")
    firefox_options.add_argument(profile_path)

    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=firefox_options)
    driver.get("https://web.whatsapp.com")
    return driver


def open_group(driver, group_name):
    wait = WebDriverWait(driver, 30)

    chat_entry = wait.until(
        EC.element_to_be_clickable((By.XPATH, f'//span[@title="{group_name}"]'))
    )
    chat_entry.click()

    try:
        header_title = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 'span[data-testid="conversation-info-header-chat-title"]')
            )
        )
        if header_title.text.strip() != group_name:
            raise RuntimeError(
                f"SAFETY CHECK FAILED: Expected '{group_name}' but header "
                f"shows '{header_title.text}'. Aborting."
            )
    except TimeoutException:
        raise RuntimeError(
            f"SAFETY CHECK FAILED: Chat header never appeared after opening "
            f"'{group_name}'. Aborting."
        )


def scroll_to_top(driver, max_scrolls=30):
    try:
        chat_panel = driver.find_element(
            By.CSS_SELECTOR, "div[data-testid='conversation-panel-messages']"
        )
    except NoSuchElementException:
        return

    last_count = 0
    for _ in range(max_scrolls):
        driver.execute_script("arguments[0].scrollTop = 0", chat_panel)
        time.sleep(0.5)
        current_count = len(driver.find_elements(
            By.CSS_SELECTOR, "div.copyable-text[data-pre-plain-text]"
        ))
        if current_count == last_count:
            break
        last_count = current_count


def read_messages(driver, group_name):
    try:
        header_title = driver.find_element(
            By.CSS_SELECTOR,
            'span[data-testid="conversation-info-header-chat-title"]'
        )
        if header_title.text.strip() != group_name:
            raise RuntimeError(
                f"SAFETY CHECK FAILED during polling: expected "
                f"'{group_name}', found '{header_title.text}'. Stopping."
            )
    except NoSuchElementException:
        raise RuntimeError(
            "SAFETY CHECK FAILED during polling: chat header not found at "
            "all. Stopping."
        )

    message_containers = driver.find_elements(
        By.CSS_SELECTOR, "div.copyable-text[data-pre-plain-text]")

    messages = []
    for container in message_containers:
        meta = container.get_attribute("data-pre-plain-text")
        match = re.match(r"\[(.*?)\]\s*(.*?):\s*$", meta)
        if not match:
            continue
        timestamp_str, sender = match.groups()

        try:
            text_element = container.find_element(
                By.CSS_SELECTOR, 'span[data-testid="selectable-text"]')
            text = text_element.text
        except Exception:
            text = ""

        messages.append({
            "sender": sender,
            "timestamp": timestamp_str,
            "text": text
        })

    return messages


def parse_wa_timestamp(timestamp_str):
    return datetime.strptime(timestamp_str, "%I:%M %p, %d/%m/%Y")


def build_seen_from_sheet(worksheet):
    records = worksheet.get_all_values()
    seen = set()
    for row in records[1:]:
        if len(row) >= 9:
            timestamp, sender, raw_text = row[0], row[1], row[8]
            seen.add((sender, timestamp, raw_text))
    return seen


def polling_loop(driver, worksheet, config, logger):
    logger.info("Loading available chat history...")
    scroll_to_top(driver)

    seen_messages = build_seen_from_sheet(worksheet)
    logger.info(
        f"Reconciled {len(seen_messages)} existing entries from the sheet."
    )
    logger.info("Now watching for purchases (including full history reconciliation)...")

    while True:
        try:
            messages = read_messages(driver, config["group_name"])

            for m in messages:
                message_id = (m["sender"], m["timestamp"], m["text"])
                if message_id in seen_messages:
                    continue

                seen_messages.add(message_id)
                try:
                    process_message(m, worksheet)
                    logger.info(
                        f"Processed message from {m['sender']} at {m['timestamp']}")
                except Exception as e:
                    logger.error(
                        f"Failed to process message from {m['sender']}: {e}")

        except RuntimeError as e:
            logger.critical(str(e))
            raise
        except Exception as e:
            logger.error(f"Polling loop error: {e}")

        time.sleep(5)


if __name__ == "__main__":
    config = load_config()
    logger = setup_logger(config["log_file"])

    logger.info(f"Starting automation for client: {config['client_name']}")

    driver = start_browser(config["profile_folder"])
    open_group(driver, config["group_name"])
    worksheet = get_sheet(config["sheet_name"], config["worksheet_name"])
    polling_loop(driver, worksheet, config, logger)
