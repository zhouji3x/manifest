#!/usr/bin/env python
import os
import unittest
from lxml import etree
from check_customer_to_project_groups import CustomersToProjectGroupsYaml


def _findManifestDtd():
    curr_dir = os.path.abspath(os.path.dirname(__file__))
    repodir = None
    while curr_dir != '/' and repodir is None:
        repodir = os.path.join(curr_dir, '.repo')
        if not os.path.isdir(repodir):
            repodir = None
            curr_dir = os.path.dirname(curr_dir)
    return os.path.join(repodir, 'repo', 'docs', 'manifest.dtd')


class CheckManifestSrcPath(object):
    """return [path,xml file containing the path] of all repo find in all xml files in '.' and 'include' folder,
       regardless of the appartenance of the xml file to the manifest of the branch"""
    project_path_list = []
    def __init__(self):
        listemanifest = CheckManifestXML()
        for manifest in listemanifest.xmlToCheck():
           manifest_tree = etree.parse(manifest)
           projects = manifest_tree.xpath("/manifest/project")
           for project in projects:
                try:
                    self.project_path_list.append([project.xpath("@path")[0],manifest])
                except IndexError:
                    print "error in file : >%s< may be project have no path ?" %(manifest)

class CheckManifestXML(object):
    EXTERNAL_ANNOTATIONS_ALLOWED = ["no", "src", "bin"]

    def _ParseManifestXml(self, path, include_root):
        root = xml.dom.minidom.parse(path)
        if not root or not root.childNodes:
            raise ManifestParseError("no root node in %s" % (path,))

        manifests_nodes = root.getElementsByTagName("manifest")
        if not manifests_nodes:
            raise ManifestParseError("no <manifest> in %s" % (path,))

        config = manifests_nodes[0]
        nodes = []
        for node in config.childNodes:
            if node.nodeName == 'include':
                name = self._reqatt(node, 'name')
                fp = os.path.join(include_root, name)
                if not os.path.isfile(fp):
                    raise ManifestParseError, \
                        "include %s doesn't exist or isn't a file" % \
                        (name,)
                try:
                    nodes.extend(self._ParseManifestXml(fp, include_root))
                # should isolate this to the exact exception, but that's
                # tricky.  actual parsing implementation may vary.
                except (KeyboardInterrupt, RuntimeError, SystemExit):
                    raise
                except Exception, e:
                    raise ManifestParseError(
                        "failed parsing included manifest %s: %s", (name, e))
            else:
              nodes.append(node)
        return nodes

    def manifestsToCheck(self):
        """ returns the list of .xml files in include folder """
        manifests = []
        for root, _, files in os.walk("include"):
            for filename in files:
                if filename.endswith(".xml"):
                    manifests.append(os.path.join(root, filename))
        return manifests

    def xmlToCheck(self):
        """ returns the list of .xml files in folder """
        manifests = []
        list_dir = [".","./include"]
        for directory_to_scan in list_dir:
           try:
               for filename in os.listdir(directory_to_scan):
                  if filename.endswith(".xml"):
                    manifests.append(os.path.join(directory_to_scan,filename))
           except OSError:
               print "\nimpossible to access directory >>%s<<\n" % (directory_to_scan)
        return manifests

    def checkManifestAgainstDtd(self, manifest, dtd):
        """ check that manifest comply with the DTD (Document Type Definition) """
        print "\nChecking %s manifest" % (manifest,)
        manifest_tree = etree.parse(manifest)
        dtd.assertValid(manifest_tree)

    def checkAllManifestsAgainstDtd(self):
        """ check that all manifests comply with the DTD (Document Type Definition) """
        dtd = etree.DTD(_findManifestDtd())
        for manifest in self.manifestsToCheck():
            self.checkManifestAgainstDtd(manifest, dtd)

    def externalCustomersFromYaml(self, customers_to_project_groups):
        """ return the list of external customers in customers_to_project_groups.yaml """
        external_customers = customers_to_project_groups["external_customers"]
        external_customers = [external_customers[customer]["short_name"] for customer in external_customers]
        # append _external to match annotation syntax
        return [customer + "_external" for customer in external_customers]

    def checkManifestExternalAnnotation(self, manifest, customers_to_project_groups):

        def _check_identical_sets(a, b, error_msg):
            delta = set(a) - set(b)
            if delta:
                raise ValueError(error_msg + ": %s" % (list(delta),))

        """ check consistency between external annotations in manifest and customer yaml file """
               print "\nimpossible to access directory >>%s<<\n" % (directory_to_scan)
        return manifests

    def checkManifestAgainstDtd(self, manifest, dtd):
        """ check that manifest comply with the DTD (Document Type Definition) """
        print "\nChecking %s manifest" % (manifest,)
        manifest_tree = etree.parse(manifest)
        dtd.assertValid(manifest_tree)

    def checkAllManifestsAgainstDtd(self):
        """ check that all manifests comply with the DTD (Document Type Definition) """
        dtd = etree.DTD(_findManifestDtd())
        for manifest in self.manifestsToCheck():
            self.checkManifestAgainstDtd(manifest, dtd)

    def externalCustomersFromYaml(self, customers_to_project_groups):
        """ return the list of external customers in customers_to_project_groups.yaml """
        external_customers = customers_to_project_groups["external_customers"]
        external_customers = [external_customers[customer]["short_name"] for customer in external_customers]
        # append _external to match annotation syntax
        return [customer + "_external" for customer in external_customers]

    def checkManifestExternalAnnotation(self, manifest, customers_to_project_groups):

        def _check_identical_sets(a, b, error_msg):
            delta = set(a) - set(b)
            if delta:
                raise ValueError(error_msg + ": %s" % (list(delta),))

        """ check consistency between external annotations in manifest and customer yaml file """
        external_customers = self.externalCustomersFromYaml(customers_to_project_groups)
        manifest_tree = etree.parse(manifest)
        print "\nChecking external annotations in %s manifest" % (manifest,)
        projects = manifest_tree.xpath("/manifest/project")
        for project in projects:
            project_name = project.xpath("@name")[0]
            project_groups = project.xpath("@groups")[0].split(",")
            if "bsp-priv" in project_groups:
                # project is PRIVATE

                # check external annotations consistency with external_customers defined in customers_to_project_groups
                annotations = project.xpath("annotation[contains(@name, '_external')]/@name")
                _check_identical_sets(external_customers,
                                      annotations,
                                      "missing annotation in %s project" % (project_name,))
                _check_identical_sets(annotations,
                                      external_customers,
                                      "additional annotation in %s project" % (project_name,))

                # check that external annotations are in EXTERNAL_ANNOTATIONS_ALLOWED
                annotations_value = project.xpath("annotation[contains(@name, '_external')]/@value")
                _check_identical_sets(annotations_value,
                                      self.EXTERNAL_ANNOTATIONS_ALLOWED,
                                      "Forbidden annotation in %s project" % (project_name,))

                # check that if one of the customer has its external annotation to 'bin', then generic customer must be set to 'bin' as well
                generic_customer = ["g_external"]
                non_generic_customers = set(external_customers) - set(generic_customer)
                project_released_as_bin = False
                project_released_as_src = False
                for customer in non_generic_customers:
                    annotation_value = project.xpath("annotation[@name='%s']/@value" % (customer,))[0]
                    if annotation_value == "bin":
                        project_released_as_bin = True
                    elif annotation_value == "src":
                        project_released_as_src = True
                generic_annotation_value = project.xpath("annotation[@name='%s']/@value" % (generic_customer[0],))[0]
                if project_released_as_bin:
                    # check that generic customer annotation is set to 'bin'
                    if generic_annotation_value != "bin":
                        raise ValueError("%s annotation must be set to 'bin' "
                                         "for %s project" %
                                         (generic_customer, project_name))
                elif project_released_as_src:
                    # check that generic customer annotation is set to 'src'
                    if generic_annotation_value != "src":
                        raise ValueError("%s annotation must be set to 'src' "
                                         "for %s project" %
                                         (generic_customer, project_name))
                else:
                    # check that generic customer annotation is set to 'no'
                    if generic_annotation_value != "no":
                        raise ValueError("%s annotation must be set to 'no' "
                                         "for %s project" %
                                         (generic_customer, project_name))

            else:
                # check that non bsp-priv projects don't have external annotations
                annotations = project.xpath("annotation[contains(@name, '_external')]/@name")
                forbidden_annotation = list(set(annotations) & set(external_customers))
                if forbidden_annotation:
                    raise ValueError("%s annotation is not allowed in %s "
                                     "project not belonging to bsp-priv group" %
                                     (forbidden_annotation, project_name))

    def checkAllPrivateManifestsExternalAnnotation(self):
        """ check consistency between external annotations in all manifests and customer yaml file """
        customers_to_project_groups_yaml = os.path.join(os.path.dirname(__file__),
                                                        "..",
                                                        "customers_to_project_groups.yaml")
        customers_to_project_groups = CustomersToProjectGroupsYaml._parseCustomersToProjectGroups(customers_to_project_groups_yaml)
        customers_to_project_groups = CustomersToProjectGroupsYaml._checkCustomersToProjectGroupsYaml(customers_to_project_groups)
        for manifest in self.manifestsToCheck():
            self.checkManifestExternalAnnotation(manifest, customers_to_project_groups)


class TestCheckManifestXML(unittest.TestCase):

    def assertRaisesWithMessage(self, exceptionClass, expectedMessage, callableObj, *args, **kw):
        try:
            callableObj(*args, **kw)
        except exceptionClass, err:
            self.assertEqual(str(err), expectedMessage)
            return
        raise Exception("%s not raised" % (exceptionClass,))

    def testCheckManifestAgainstDtdOk(self):
        dtd = etree.DTD(_findManifestDtd())
        manifest = os.path.join(os.path.dirname(__file__), "test_db", "manifestOk.xml")
        c = CheckManifestXML()
        c.checkManifestAgainstDtd(manifest, dtd)

    def oneTestCheckManifestManifestWrongAnnotationValue(self, manifest,
                                                         expected_result,
                                                         expected_error_message=None):
        customers_to_project_groups_yaml = os.path.join(os.path.dirname(__file__),
                                                        "test_db",
                                                        "customers_to_project_groups.yaml")
        customers_to_project_groups = CustomersToProjectGroupsYaml._parseCustomersToProjectGroups(customers_to_project_groups_yaml)
        customers_to_project_groups = CustomersToProjectGroupsYaml._checkCustomersToProjectGroupsYaml(customers_to_project_groups)
        c = CheckManifestXML()
        if isinstance(expected_result, Exception):
            self.assertRaisesWithMessage(type(expected_result), expected_error_message, c.checkManifestExternalAnnotation, manifest, customers_to_project_groups)
        else:
            c.checkManifestExternalAnnotation(manifest, customers_to_project_groups)

    def testCheckManifestManifestWrongAnnotationValue(self):
        manifest = os.path.join(os.path.dirname(__file__),
                                "test_db",
                                "manifestWrongAnnotationValue.xml")
        self.oneTestCheckManifestManifestWrongAnnotationValue(
            manifest, ValueError(),
            "Forbidden annotation in my/path/to/projectB project: ['forbidden']")

    def testCheckManifestManifestMissingAnnotation(self):
        manifest = os.path.join(os.path.dirname(__file__),
                                "test_db",
                                "manifestMissingAnnotation.xml")
        self.oneTestCheckManifestManifestWrongAnnotationValue(
            manifest, ValueError(),
            "missing annotation in my/path/to/projectB project: ['bbb_external']")

    def testCheckManifestManifestAdditionalAnnotation(self):
        manifest = os.path.join(os.path.dirname(__file__),
                                "test_db",
                                "manifestAdditionalAnnotation.xml")
        self.oneTestCheckManifestManifestWrongAnnotationValue(
            manifest, ValueError(),
            "additional annotation in my/path/to/projectB project: ['ccc_external']")

    def testCheckManifestManifestNonPrivateProjectWithAnnotation(self):
        manifest = os.path.join(os.path.dirname(__file__),
                                "test_db",
                                "manifestNonPrivateProjectWithAnnotation.xml")
        self.oneTestCheckManifestManifestWrongAnnotationValue(
            manifest, ValueError(),
            "['bbb_external', 'a_external', 'g_external'] annotation is not "
            "allowed in my/path/to/projectB project not belonging to bsp-priv group")

    def testCheckManifestManifestGenericCustomerAnnotationToBin(self):
        manifest = os.path.join(os.path.dirname(__file__),
                                "test_db",
                                "manifestGenericCustomerAnnotationToBin.xml")
        self.oneTestCheckManifestManifestWrongAnnotationValue(
            manifest, ValueError(),
            "['g_external'] annotation must be set to 'bin' for "
            "my/path/to/projectB project")

    def testCheckManifestManifestGenericCustomerAnnotationToNo(self):
        manifest = os.path.join(os.path.dirname(__file__),
                                "test_db",
                                "manifestGenericCustomerAnnotationToNo.xml")
        self.oneTestCheckManifestManifestWrongAnnotationValue(
            manifest, ValueError(),
            "['g_external'] annotation must be set to 'no' for "
            "my/path/to/projectB project")

    def testCheckManifestManifestGenericCustomerAnnotationToSrc(self):
        manifest = os.path.join(os.path.dirname(__file__),
                                "test_db",
