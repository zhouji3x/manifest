#!/usr/bin/env python
import unittest
from check_reviewers_verifiers_yaml_config import TestCheckVerifiersAndReviewers
from check_reviewers_verifiers_yaml_config import TestCheckCommitedVerifiersAndReviewersOnGerrit
from check_reviewers_verifiers_yaml_config import TestCheckCommitedVerifiersAndReviewers

def main():
    error = False
    for tc in [TestCheckCommitedVerifiersAndReviewers,
               TestCheckCommitedVerifiersAndReviewersOnGerrit,
               TestCheckVerifiersAndReviewers]:
        suite = unittest.TestLoader().loadTestsFromTestCase(tc)
        error = error or not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()

    if error:
        raise Exception("Unit test failed on manifest. Please check logs and fix the issue")

if __name__ == "__main__":
    main()
