import os
import requests


def save_from_tg(token, f_info, f_name, dp):
    res = requests.get(
        f"https://api.telegram.org/file/bot{token}/{f_info.file_path}"
    )

    fp = os.path.join(dp, f_name)
    with open(fp, 'wb') as f:
        f.write(res.content)

    return fp
