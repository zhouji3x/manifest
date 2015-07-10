#!/usr/bin/env python
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))
import unittest
import yaml


class CustomersToProjectGroupsYaml(object):

    @staticmethod
    def _parseCustomersToProjectGroups(yaml_file):
        config = open(yaml_file).read()
        return yaml.load(config)

    @staticmethod
    def _checkCustomersToProjectGroupsYaml(customers_to_project_groups):

        def _check_type_and_duplicates(mylist):
            if not isinstance(mylist, list):
                raise TypeError("%s must be a list" % (mylist,))
            if len(mylist) != len(set(mylist)):
                raise ValueError("There are duplicated elements in %s" % (mylist,))

        generic_groups = customers_to_project_groups["generic_groups"]
        _check_type_and_duplicates(generic_groups)
        platform_groups = customers_to_project_groups["platform_groups"]
        _check_type_and_duplicates(platform_groups)
        all_groups = generic_groups + platform_groups
        _check_type_and_duplicates(all_groups)

        external_customers = customers_to_project_groups["external_customers"]
        all_groups_set = set(all_groups)
        for customer in external_customers:
            name = external_customers[customer]["name"]
            include_groups = external_customers[customer]["include_groups"]
            _check_type_and_duplicates(include_groups)
            exclude_groups = external_customers[customer]["exclude_groups"]
            _check_type_and_duplicates(exclude_groups)
            all_customer_groups = include_groups + exclude_groups
            _check_type_and_duplicates(all_customer_groups)

            all_customer_groups_set = set(all_customer_groups)
            if (all_customer_groups_set - all_groups_set):
                raise ValueError("Customers group config: unexpected groups in '%s' customer 'include_groups' or 'exclude_groups': %s"
                                  % (name, list(all_customer_groups_set - all_groups_set)))
            if (all_groups_set - all_customer_groups_set):
                raise ValueError("Customers group config: missing groups in '%s' customer 'include_groups' or 'exclude_groups': %s"
                                  % (name, list(all_groups_set - all_customer_groups_set)))

        return customers_to_project_groups


class TestCustomersToProjectGroupsYaml(unittest.TestCase):

    def testParseCustomersToProjectGroups(self):
        r = os.path.join(os.path.dirname(__file__), "test_db", "customers_to_project_groups.yaml")
        e = CustomersToProjectGroupsYaml()
        c = e._parseCustomersToProjectGroups(r)
        self.assertEqual(c, {'external_customers':
                               {'a_customer':
                                {'exclude_groups': ['g2', 'g5'],
                                 'name': 'customerA',
                                 'short_name': 'a',
                                 'include_groups': ['g1', 'g3', 'g4', 'g6']},
                                'bbb_customer':
                                {'exclude_groups': ['g2', 'g3', 'g4', 'g5'],
                                 'name': 'customerBbb',
                                 'short_name': 'bbb',
                                 'include_groups': ['g1', 'g6']},
                                'g_customer':
                                {'exclude_groups': ['g1', 'g2', 'g5'],
                                 'name': 'customerG',
                                 'short_name': 'g',
                                 'include_groups': ['g3', 'g4', 'g6']}},
                                'platform_groups': ['g5', 'g6'],
                                'generic_groups': ['g1', 'g2', 'g3', 'g4']})
        check = CustomersToProjectGroupsYaml._checkCustomersToProjectGroupsYaml(c)
        self.assertEqual(check, c)

    def testParseCustomersToProjectGroups_MissingFile(self):
        r = os.path.join(os.path.dirname(__file__), "test_db", "customers_to_project_groups_missing_file.yaml")
        e = CustomersToProjectGroupsYaml()
        self.assertRaises(IOError, e._parseCustomersToProjectGroups, r)

    def testParseCustomersToProjectGroups_InvalidFile(self):
        r = os.path.join(os.path.dirname(__file__), "test_db", "customers_to_project_groups_invalid_file.yaml")
        e = CustomersToProjectGroupsYaml()
        self.assertRaises(Exception, e._parseCustomersToProjectGroups, r)

    def testParseCustomersToProjectGroups_InvalidGroup(self):
        r = os.path.join(os.path.dirname(__file__), "test_db", "customers_to_project_groups_invalid_group.yaml")
        e = CustomersToProjectGroupsYaml()
        c = e._parseCustomersToProjectGroups(r)
        self.assertRaises(TypeError, CustomersToProjectGroupsYaml._checkCustomersToProjectGroupsYaml, c)

    def testcheckCustomersToProjectGroupsYaml_Duplicates(self):
        r = os.path.join(os.path.dirname(__file__), "test_db", "customers_to_project_groups_duplicates.yaml")
        e = CustomersToProjectGroupsYaml()
        c = e._parseCustomersToProjectGroups(r)
        self.assertRaises(ValueError, CustomersToProjectGroupsYaml._checkCustomersToProjectGroupsYaml, c)

    def testcheckCustomersToProjectGroupsYaml_Duplicates2(self):
        r = os.path.join(os.path.dirname(__file__), "test_db", "customers_to_project_groups_duplicates2.yaml")
        e = CustomersToProjectGroupsYaml()
        c = e._parseCustomersToProjectGroups(r)
        self.assertRaises(ValueError, CustomersToProjectGroupsYaml._checkCustomersToProjectGroupsYaml, c)

    def testcheckCustomersToProjectGroupsYaml_Duplicates3(self):
        r = os.path.join(os.path.dirname(__file__), "test_db", "customers_to_project_groups_duplicates3.yaml")
        e = CustomersToProjectGroupsYaml()
        c = e._parseCustomersToProjectGroups(r)
        self.assertRaises(ValueError, CustomersToProjectGroupsYaml._checkCustomersToProjectGroupsYaml, c)

    def testcheckCustomersToProjectGroupsYaml_MissingGroups(self):
        r = os.path.join(os.path.dirname(__file__), "test_db", "customers_to_project_groups_missing_groups.yaml")
        e = CustomersToProjectGroupsYaml()
        c = e._parseCustomersToProjectGroups(r)
        self.assertRaises(ValueError, CustomersToProjectGroupsYaml._checkCustomersToProjectGroupsYaml, c)

    def testcheckCustomersToProjectGroupsYaml_AdditionalGroups(self):
        r = os.path.join(os.path.dirname(__file__), "test_db", "customers_to_project_groups_additional_groups.yaml")
        e = CustomersToProjectGroupsYaml()
        c = e._parseCustomersToProjectGroups(r)
        self.assertRaises(ValueError, CustomersToProjectGroupsYaml._checkCustomersToProjectGroupsYaml, c)


def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCustomersToProjectGroupsYaml)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    main()
