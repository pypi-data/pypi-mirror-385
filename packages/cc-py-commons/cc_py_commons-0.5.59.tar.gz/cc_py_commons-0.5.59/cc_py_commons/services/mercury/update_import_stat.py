import os
import requests

MERCURY_URL = os.environ.get("MERCURY_URL")
MERCURY_TOKEN = os.environ.get("MERCURY_TOKEN")

from cc_py_commons.utils.logger_v2 import logger


def execute(updated_data, import_stat_id):
  url = f"{MERCURY_URL}/importStats/{import_stat_id}"
  token = f"Bearer {MERCURY_TOKEN}"
  headers = {
    "Authorization": token
  }
  response = requests.put(url, json=updated_data, headers=headers)
  if response.status_code not in [200, 201]:
    logger.error(f"Failed to update import stat {updated_data} - {response.status_code}:{response.text}")
    return None
  else:
    return response.json()
