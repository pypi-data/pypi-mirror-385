import re
import json

def parse_json(text):
    """
    ```json ... ```
    """
    pattern = r"```json\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    return None


def parse_output(text):
    pattern = r"<output>(.*?)</output>"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return text.strip()


def parse_mark(text, mark):
    pattern = rf"<{mark}>(.*?)</{mark}>"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return text.strip()
