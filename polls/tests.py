#-*- coding: utf-8 -*-
import signal
import time

from contextlib import contextmanager
from selenose.cases import LiveServerTestCase

class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException, "Timed out!"
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

class AdminTestCase(LiveServerTestCase):

    def test_login(self):
        # Open the administration page
        self.driver.get(self.live_server_url + '/admin/')
        # Enter the name of the user
        username = self.driver.find_element_by_id('id_username')
        with time_limit(10):
            username.send_keys('admin')
        # Get the password input
        password = self.driver.find_element_by_id('id_password')
        # Type password
        with time_limit(10):
            password.send_keys('admin')
        # Submit the form
        password.submit()
        # Load page
        time.sleep(2)
        # Check that welcomed
        self.assertTrue(self.driver.find_element_by_id('user-tools').text.startswith('Welcome'))

class PollsTestCase(LiveServerTestCase):

    def test_vote(self):
        # Open the polls page
        self.driver.get(self.live_server_url + '/polls/')
        # Get the link to the poll "ShiningPanda is a..."
        poll = self.driver.find_element_by_link_text('ShiningPanda is a...')
        # Click on the link
        poll.click()
        # Load page
        time.sleep(2)
        # Get the available choices
        choices = self.driver.find_elements_by_name('choice')
        # Check that only three choices: "Hosted CI service?", "Consulting firm?" and "Both!"
        self.assertEquals(3, len(choices))
        # Select "Both!"
        choices[2].click()
        # Submit the form
        choices[2].submit()
        # Get the poll results
        lis = self.driver.find_elements_by_tag_name('li')
        # Check that results are displayed for each choices (three choices)
        self.assertEquals(3, len(lis))
        # Check that "Hosted CI service?" has no votes
        self.assertEquals('Hosted CI service? -- 0 votes', lis[0].text)
        # Check that "Consulting firm?" has no votes
        self.assertEquals('Consulting firm? -- 0 votes', lis[1].text)
        # Check that our vote for "Both!" was well stored
        self.assertEquals('Both! -- 1 vote', lis[2].text)

