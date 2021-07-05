
def location_by_id(value):
    """通过唯一id定位"""
    code = "temporary_button = WebDriverWait(self.driver, self.explicit_wait_timeout, self.explicit_wait_poll_time).until(EC.visibility_of_element_located((By.ID, '{}')))\n".format(value)
    # 隐式等待代码 执行流程时使用
    code1 = "temporary_button = WebDriverWait(self.driver, self.explicit_wait_timeout, self.explicit_wait_poll_time).until(EC.visibility_of_any_elements_located((By.ID, '{}')))\n".format(value)
    # 断言代码 断言验证时使用
    return code, code1


def location_by_class_name(value):
    """通过class_name定位"""
    code = "temporary_button = WebDriverWait(self.driver, self.explicit_wait_timeout, self.explicit_wait_poll_time).until(EC.visibility_of_element_located((By.CLASS_NAME, '{}')))\n".format(value)
    code1 = "temporary_button = WebDriverWait(self.driver, self.explicit_wait_timeout, self.explicit_wait_poll_time).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, '{}')))\n".format(value)
    return code, code1


def location_by_tag_name(value):
    """通过tag_name定位"""
    code = "temporary_button = WebDriverWait(self.driver, self.explicit_wait_timeout, self.explicit_wait_poll_time).until(EC.visibility_of_element_located((By.TAG_NAME, '{}')))\n".format(value)
    code1 = "temporary_button = WebDriverWait(self.driver, self.explicit_wait_timeout, self.explicit_wait_poll_time).until(EC.visibility_of_any_elements_located((By.TAG_NAME, '{}')))\n".format(value)
    return code, code1


def location_by_link_text(value):
    """通过link_text定位(精确匹配超链接载体)"""
    code = "temporary_button = WebDriverWait(self.driver, self.explicit_wait_timeout, self.explicit_wait_poll_time).until(EC.visibility_of_element_located((By.LINK_TEXT, '{}')))\n".format(value)
    code1 = "temporary_button = WebDriverWait(self.driver, self.explicit_wait_timeout, self.explicit_wait_poll_time).until(EC.visibility_of_any_elements_located((By.LINK_TEXT, '{}')))\n".format(value)
    return code, code1


def location_by_xpath(value):
    """通过xpath定位"""
    code = "temporary_button = WebDriverWait(self.driver, self.explicit_wait_timeout, self.explicit_wait_poll_time).until(EC.visibility_of_element_located((By.XPATH, '{}')))\n".format(value)
    code1 = "temporary_button = WebDriverWait(self.driver, self.explicit_wait_timeout, self.explicit_wait_poll_time).until(EC.visibility_of_any_elements_located((By.XPATH, '{}')))\n".format(value)
    return code, code1


def location_by_css_selector(value):
    """通过css选择器定位"""
    code = "temporary_button = WebDriverWait(self.driver, self.explicit_wait_timeout, self.explicit_wait_poll_time).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '{}')))\n".format(value)
    code1 = "temporary_button = WebDriverWait(self.driver, self.explicit_wait_timeout, self.explicit_wait_poll_time).until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, '{}')))\n".format(value)
    return code, code1


def location_by_partial_link_text(value):
    """通过link_text定位(模糊匹配超链接载体)"""
    code = "temporary_button = WebDriverWait(self.driver, self.explicit_wait_timeout, self.explicit_wait_poll_time).until(EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, '{}')))\n".format(value)
    code1 = "temporary_button = WebDriverWait(self.driver, self.explicit_wait_timeout, self.explicit_wait_poll_time).until(EC.visibility_of_any_elements_located((By.PARTIAL_LINK_TEXT, '{}')))\n".format(value)
    return code, code1


def location_switch_iframe_by_index(value):
    """通过下标切换switch"""
    code = "temporary_button = int('{}')\n".format(value)
    code1 = "temporary_button = int('{}')\n".format(value)
    return code, code1


