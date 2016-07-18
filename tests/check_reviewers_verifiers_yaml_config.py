#!/usr/bin/env python
import os
import json
import shlex
import subprocess
import unittest
import urllib2
from manifest_xutils import yaml

MAGIC_PREFIX = ")]}'"


class CheckVerifiersAndReviewers(object):

    def loadVerifiersAndReviewers(self, usersfiles):
        """
        Load all verifiers and reviewers with their domains
        @rtype: dict
        """
        users = {}
        for f in usersfiles:
            fn = os.path.join(os.path.dirname(__file__), "..", f)
            with open(fn) as opened_f:
	        allfileUsers = yaml.load(opened_f.read(), Loader=yaml.OrderedMapAndDuplicateCheckLoader)
            for user in allfileUsers:
                users.update({user: [allfileUsers[user], f]})
        return users

    def getGerritGroupPerUser(self, user):
        """
        return Gerrit group list per user
        """
        command = "ssh android.intel.com gerrit ls-groups -u %s" % (user,)
        args = shlex.split(command)
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = proc.communicate()[0]
        groups = output.split('\n')
        return groups

    def checkGerritUsers(self, usersfiles):
        """
        For each user specified, check if its email matches the user settings in Gerrit.
        Return the list of invalid users
        """
        users = self.loadVerifiersAndReviewers(usersfiles)
        invalid_users = []
        for user in users:
            url = "https://android.intel.com/accounts/%s" % (user,)
            try:
                data = urllib2.urlopen(url).read()
                _, _, account = data.partition(MAGIC_PREFIX)
                account = json.loads(account)
                email = account['email']
                if user != email:
                    invalid_users.append([user, users[user][1]])
                    print ("\nInvalid user in yaml:\n"
                           "Got: %s\n"
                           "Expected from Gerrit settings: %s\n" % (user, email))
            except urllib2.HTTPError:
                invalid_users.append([user, users[user][1]])
        return invalid_users

    def checkValidIntelEmail(self, usersfiles):
        """
        Each user need to have an email format with "@intel.com" or "@windriver.com"
        """
        invalid_users = []
        users = self.loadVerifiersAndReviewers(usersfiles)
        for user in users:
            if not user.endswith("@intel.com") and not user.endswith("@windriver.com") and not user.startswith("ldap"):
                invalid_users.append([user, users[user][1]])
        return invalid_users

    def checkValidDomains(self, usersfiles, sourcefile):
        """
        Each domain assigned to a user need to be defined
        """
        fn = os.path.join(os.path.dirname(__file__), "..", sourcefile)
        domains = yaml.load(open(fn))
        users = self.loadVerifiersAndReviewers(usersfiles)
        invalidDomains = []
        for user in users:
            for domainVerifier in users[user][0]:
                if domainVerifier not in domains:
                    invalidDomains.append([domainVerifier, user, users[user][1]])
        return invalidDomains

class CheckVerifiersAndReviewersOnGerrit(CheckVerifiersAndReviewers):

    def checkGerritGroupPerUser(self, usersfiles):
        """
        Users are registred in Gerrit under groups
        This test verifies that each user belongs to groups defined
        this check show that user exist or not with good groups in gerrit
        if no group found for a user gerrit send an error
        """
        users = self.loadVerifiersAndReviewers(usersfiles)
        for user in users:
            groups = self.getGerritGroupPerUser(user)
            bad_groups = []
            if "reviewer" in users[user][1]:
                for domain in users[user][0]:
                    if not any("reviewers-domain-%s" % (domain) in group for group in groups):
                        bad_groups.append([user, domain, users[user][1]])
            if "verifier" in users[user][1]:
                for domain in users[user][0]:
                    if not any("maintainers-domain-%s" % (domain) in group for group in groups):
                        bad_groups.append([user, domain, users[user][1]])
        return bad_groups


class TestCheckVerifiersAndReviewers(CheckVerifiersAndReviewersOnGerrit, CheckVerifiersAndReviewers, unittest.TestCase):

    def testLoadVerifiersAndReviewers(self):
        """
        verify that function load every users
        """
        usersfilesdb = ["tests/test_db/reviewers-to-domain.yaml"]
        users = self.loadVerifiersAndReviewers(usersfilesdb)
        expected_users = {'valid.reviewer@intel.com': [['AOSP', 'KERNEL'],
                                                        'tests/test_db/reviewers-to-domain.yaml'],
                           'invalid.reviewer@itl.com': [['AOSP', 'KERNEL', 'INVALID_DOMAIN'],
                                                         'tests/test_db/reviewers-to-domain.yaml'],
                           'xavier.delas@intel.com': [['AOSP'],
                                                         'tests/test_db/reviewers-to-domain.yaml']}

        self.assertEqual(users, expected_users, "Error in expected users")

    def testCheckValidIntelEmail(self):
        usersfilesdb = ["tests/test_db/reviewers-to-domain.yaml"]
        invalid_users = self.checkValidIntelEmail(usersfilesdb)
        self.assertEqual(invalid_users,
                         [['invalid.reviewer@itl.com', 'tests/test_db/reviewers-to-domain.yaml']],
                         msg="Error invalid users:%s" % (invalid_users,))

    def testCheckValidDomains(self):
        usersfilesdb = ["tests/test_db/reviewers-to-domain.yaml"]
        sourcefiledb = "tests/test_db/source-to-domain.yaml"
        invalidDomains = self.checkValidDomains(usersfilesdb, sourcefiledb)
        self.assertEqual(invalidDomains,
                         [['INVALID_DOMAIN', 'invalid.reviewer@itl.com', 'tests/test_db/reviewers-to-domain.yaml']],
                         msg="Error invalid domains:%s" % (invalidDomains,))

    def testCheckGerritUsers(self):
        usersfilesdb = ["tests/test_db/reviewers-to-domain.yaml"]
        invalid_users = self.checkGerritUsers(usersfilesdb)
        self.assertEqual(invalid_users,
                         [['valid.reviewer@intel.com', 'tests/test_db/reviewers-to-domain.yaml'],
                         ['invalid.reviewer@itl.com', 'tests/test_db/reviewers-to-domain.yaml']],
                         msg="Error invalid users in GERRIT:%s" % (invalid_users,))

class TestCheckCommitedVerifiersAndReviewers(CheckVerifiersAndReviewersOnGerrit, CheckVerifiersAndReviewers, unittest.TestCase):

    def testCheckValidIntelEmail(self):
        usersfiles = ["verifiers-to-domain.yaml", "reviewers-to-domain.yaml", "leader-to-domain.yaml"]
        invalid_users = self.checkValidIntelEmail(usersfiles)
        self.assertEqual(invalid_users, [], msg="Error invalid users:%s" % (invalid_users,))

    def testCheckValidDomains(self):
        usersfiles = ["verifiers-to-domain.yaml", "reviewers-to-domain.yaml"]
        sourcefile = "source-to-domain.yaml"
        invalidDomains = self.checkValidDomains(usersfiles, sourcefile)
        self.assertEqual(invalidDomains, [], msg="Error invalid domains:%s" % (invalidDomains,))

class TestCheckCommitedVerifiersAndReviewersOnGerrit(CheckVerifiersAndReviewersOnGerrit, unittest.TestCase):

    def testCheckGerritUsers(self):
        usersfiles = ["verifiers-to-domain.yaml", "reviewers-to-domain.yaml"]
        invalid_users = self.checkGerritUsers(usersfiles)
        self.assertFalse(invalid_users)

    def testCheckGerritGroupPerUser(self):
        usersfiles = ["verifiers-to-domain.yaml", "reviewers-to-domain.yaml"]
        bad_groups = self.checkGerritGroupPerUser(usersfiles)
        self.assertEqual(bad_groups, [], msg="On gerrit check found invalids domains:%s" % (bad_groups,))


def main():
    error = False
    for tc in [TestCheckVerifiersAndReviewers]:
        suite = unittest.TestLoader().loadTestsFromTestCase(tc)
        error = error or not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()

    if error:
        raise Exception("Unit test failed on manifest. Please check logs and fix the issue")

if __name__ == "__main__":
    main()
