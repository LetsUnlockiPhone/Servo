# -*- coding: utf-8 -*-
# Copyright (c) 2013, First Party Software
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, 
# this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, 
# this list of conditions and the following disclaimer in the documentation 
# and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT 
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF 
# SUCH DAMAGE.

import os
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.url = 'http://localhost:8000/checkin/'
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)
        self.browser.get(self.url)

    def tearDown(self):
        self.browser.quit()

    def fill_device_details(self):
        self.browser.find_element_by_id('id_username').send_keys('username')
        self.browser.find_element_by_id('id_password').send_keys('password')
        self.browser.find_element_by_id("id_pop").send_keys("/tmp/image.png")

    def fill_checklist(self):
        btn = self.browser.find_element_by_class_name('btn-default')
        btn.click()
        btn = self.browser.find_element_by_class_name('btn-default')
        btn.click()
        btn = self.browser.find_element_by_class_name('btn-default')
        btn.click()

    def fill_problem_description(self):
        problem_field = self.browser.find_element_by_id('id_issue_description')
        problem_field.send_keys("Mary had a little lamb")
        self.browser.find_element_by_id("id_pop").send_keys("/tmp/image.png")

    def fill_contact_fields(self):
        field = self.browser.find_element_by_id('id_fname')
        field.send_keys('Filipp')
        field = self.browser.find_element_by_id('id_lname')
        field.send_keys('Lepalaan')
        field = self.browser.find_element_by_id('id_email')
        field.send_keys('filipp@mac.com')
        field = self.browser.find_element_by_id('id_phone')
        field.send_keys('358451202717')
        field = self.browser.find_element_by_id('id_city')
        field.send_keys('Helsinki')
        field = self.browser.find_element_by_id('id_postal_code')
        field.send_keys('00500')
        field = self.browser.find_element_by_id('id_address')
        field.send_keys('Kustaankatu 2 C 96')
        field = self.browser.find_element_by_id('id_agree_to_terms')
        field.click()

    def _test_visitor_can_check_status(self):
        btn = self.browser.find_element_by_class_name('btn-default')
        btn.click()
        field = self.browser.find_element_by_id('id_code')
        field.send_keys("12019537")
        field.send_keys(Keys.ENTER)
        self.assertEqual("Repair Status", self.browser.title)

    def _test_can_checkin_wo_sn(self):
        self.browser.find_element_by_class_name('btn-primary').click()
        # customer has no serial number, chooses device
        self.browser.find_element_by_id('id_choose_device').click()
        self.browser.find_element_by_id('id_macbookpro').click()
        self.fill_device_details()
        self.next()
        self.fill_problem_description()
        self.next()
        #self.fill_checklist()
        #self.next()
        self.fill_contact_fields()
        # Submit the repair
        self.next()
        # Check that it actually worked
        btn = self.browser.find_element_by_class_name('btn-large')
        self.assertEqual(btn.text, 'Print')

    def test_can_checkin_sn(self):
        # Customer logs in to check-in
        self.assertIn('Service Order Check-In', self.browser.title)

        # customer checks warranty status...
        snfield = self.browser.find_element_by_id('id_sn')
        snfield.send_keys('C02GV550DJWV')
        snfield.send_keys(Keys.ENTER)
        self.fill_device_details()

        # ... enters problem description
        self.fill_problem_description()

        # Customer fills out her contact details
        self.fill_contact_fields()

        # Customer fills in the condition
        field = self.browser.find_element_by_id('id_condition')
        field.send_keys('Like new')

        # Submit the repair
        submit_button = self.browser.find_element_by_id('id_btn_submit')
        submit_button.click()

        # Check that it actually worked
        btn = self.browser.find_element_by_class_name('btn-large')
        self.assertEqual(btn.text, 'Print')


if __name__ == '__main__':
    unittest.main()
