#!/usr/bin/env python
import unittest
from check_customer_to_project_groups import TestCustomersToProjectGroupsYaml
from check_manifest_xml import TestCheckManifestXML
from check_aosp_domains import TestAospDomains
from check_to_domain_yaml_config import TestToDomainYamlConfig
from check_reviewers_verifiers_yaml_config import TestCheckVerifiersAndReviewers
from check_reviewers_verifiers_yaml_config import TestCheckCommitedVerifiersAndReviewers


def main():
    error = False
    for tc in [TestCustomersToProjectGroupsYaml,
               TestCheckManifestXML,
               TestToDomainYamlConfig,
               #TestAospDomains,
               TestCheckVerifiersAndReviewers,
               TestCheckCommitedVerifiersAndReviewers]:
        suite = unittest.TestLoader().loadTestsFromTestCase(tc)
        error = error or not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()

    if error:
        raise Exception("Unit test failed on manifest. Please check logs and fix the issue")

if __name__ == "__main__":
    main()
