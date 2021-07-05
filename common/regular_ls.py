# 正则存贮

# ip地址正则
REGEX_IP = '^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5]).(\d{1,2}|1\d\d|2[0-4]\d|25[0-5]).(\d{1,2}|1\d\d|2[0-4]\d|25[0-5]).(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$'
# 数字和字母组合，不允许纯数字 以字母开头
REGEX_PY_MODEL = r"^[a-zA-Z]{1}[\da-zA-Z_].*"
# 文件名非法检测 文件名 excel
REGEX_FOLD = r"[\\\\/:*?\"<>|]"



if __name__ == "__main__":
    import re
    if re.compile(REGEX_FOLD).search('213>.xlsx'):
        print(1)
