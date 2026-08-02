from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
import time
import os
import re
from datetime import datetime

from main import process_message
from Sheets_connector import get_sheet
from config_loader import load_config
from state_manager import load_state, save_state
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
    time.sleep(10)
    chat_entry = driver.find_element(
        By.XPATH, f'//span[@title="{group_name}"]')
    chat_entry.click()
    time.sleep(2)


def read_messages(driver):
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


def polling_loop(driver, worksheet, config, logger):
    seen_messages = load_state(config["state_file"])
    logger.info(f"Loaded {len(seen_messages)} previously logged messages.")
    logger.info("Now watching for purchases (including existing history)...")

    while True:
        try:
            messages = read_messages(driver)

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

                save_state(config["state_file"], seen_messages)

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
