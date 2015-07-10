#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))
import unittest
import yaml
import re
from textwrap import dedent
from StringIO import StringIO

CATEGORIES = ['aosp improvement', 'device enablement', 'feature differentiation']

AOSP_REPO = "a/aosp/platform/bionic"


class TestAospDomains(unittest.TestCase):

    def testParseToDomainConfig(self):
        fn = os.path.join(os.path.dirname(__file__), "..", "aosp_domains.yaml")
        domains = yaml.load(open(fn))
        for d, subdomains in domains.iteritems():
            if subdomains:
                for sd, parms in subdomains.iteritems():
                    for c in parms["Categories"]:
                        self.assertTrue(c in CATEGORIES,
                                        "invalid category %s for domain %s-%s" % (c, d, sd) +
                                        "\nAvailable:" + str(CATEGORIES)
                                        )


class TestCheckPatch(unittest.TestCase):

    def assertRaisesRegexp(self, expected_exception, expected_regexp,
                           callable_obj=None, *args, **kwargs):
        """Asserts that the message in a raised exception matches a regexp.
        simplified port from python 2.7
        """
        try:
            callable_obj(*args, **kwargs)
        except expected_exception, exc_value:
            if isinstance(expected_regexp, basestring):
                expected_regexp = re.compile(expected_regexp)
            if not expected_regexp.search(str(exc_value)):
                raise self.failureException('"%s" does not match "%s"' %
                                            (expected_regexp.pattern, str(exc_value)))
        else:
            if hasattr(expected_exception, '__name__'):
                excName = expected_exception.__name__
            else:
                excName = str(expected_exception)
            raise self.failureException, "%s not raised" % excName

    def oneTest(self, commit_comment, expectedFail=None, repository="/not/aosp"):
        patch_trailer = """
                        ---

                         foo/bar.py     |   29 ++++++++++++++++++++
                         3 files changed, 100 insertions(+), 4 deletions(-)

                        diff --git a/foo/bar.py b/foo/bar.py
                        index 5844f66..ef9840b 100644
                        """
        patch = dedent(commit_comment).strip() + "\n" + dedent(patch_trailer).strip() + "\n"
        patch = StringIO(patch)
        import imp
        imp.load_source("checkpatch", os.path.join(os.path.dirname(__file__),
                                                   "..", "scripts", "global_checkpatch"))
        from checkpatch import main

        class CheckPatchFail(Exception):
            pass

        def fail(msg, *args):
            raise CheckPatchFail(msg % args)
        if expectedFail:
            self.assertRaisesRegexp(CheckPatchFail, re.compile(expectedFail),
                                    main, patch, fail, repository)
        else:
            main(patch, fail, repository)

    def testSeveralTripleDash(self):
        self.oneTest("""
                      myPatch

                      ---

                      blabla
                      """, "Commit comment contains line with only '---'!")

    def testLastParagraph(self):
        self.oneTest("""
                      myPatch

                      Signed-off-by: me
                      blabla
                      """,
                     "last paragraph should only contain metadata but there is the line")
        self.oneTest("""
                      myPatch

                      Signed-off-by: me
                      """, None)

    def testAospNoCategory(self):
        self.oneTest("""
                      myPatch

                      Signed-off-by: me
                      """,
                     "Missing 'Category' tag",
                     AOSP_REPO)

    def testAospNoCategory2(self):
        self.oneTest("""
                      myPatch

                      Signed-off-by: me
                      """,
                     "AOSP patch should be properly categorized.",
                     AOSP_REPO)

    def testAospWaiver(self):
        self.oneTest("""
                      myPatch

                      Category: engineering
                      Signed-off-by: me
                      """, None,
                     AOSP_REPO)

    def testAospBadOrder(self):
        self.oneTest("""
                      myPatch

                      Signed-off-by: me
                      Category: engineering
                      """,
                     "last paragraph metadata should have proper order:Category: "
                     "engineering should be before Signed-off-by",
                     AOSP_REPO)

    def testAospMissingOrigin(self):
        self.oneTest("""
                      myPatch

                      Category: device enablement
                      Domain: CWS.BT-Common
                      Signed-off-by: me
                      """,
                     "Missing Origin tag",
                     AOSP_REPO)

    def testAospBadDomain(self):
        self.oneTest("""
                      myPatch

                      Category: feature differentiation
                      Domain: bad
                      Origin: internal
                      Upstream-Candidate: yes
                      Signed-off-by: me
                      """,
                     "Domain must be composed of FTSubsystem and Target separated by a dash",
                     AOSP_REPO)

    def testAospBadDomain2(self):
        self.oneTest("""
                      myPatch

                      Category: feature differentiation
                      Domain: foo-bar
                      Origin: internal
                      Upstream-Candidate: yes
                      Signed-off-by: me
                      """,
                     "unknown FTSubsystem: foo, known: AOSP AOSP.Connectivity",
                     AOSP_REPO)

    def testAospBadDomain3(self):
        self.oneTest("""
                      myPatch

                      Category: feature differentiation
                      Domain: CWS.BT-foo
                      Origin: internal
                      Upstream-Candidate: yes
                      Signed-off-by: me
                      """,
                     "unknown target: foo for FTSubsystem CWS.BT, known: ",
                     AOSP_REPO)

    def testAospBadCategory(self):
        self.oneTest("""
                      myPatch

                      Category: feature differentiation
                      Domain: CWS.BT-Common
                      Origin: internal
                      Upstream-Candidate: yes
                      Signed-off-by: me
                      """,
                     "forbidden category: feature differentiation for Domain CWS.BT-Common,"
                     " allowed: device enablement",
                     AOSP_REPO)

    def testAospBadOrigin(self):
        self.oneTest("""
                      myPatch

                      Category: device enablement
                      Domain: CWS.BT-Common
                      Origin: myorigin
                      Upstream-Candidate: yes
                      Signed-off-by: me
                      """,
                     r"bad origin: myorigin allowed \(regular expressions\): ",
                     AOSP_REPO)

    def testAospBadUpstreamCandidate(self):
        self.oneTest("""
                      myPatch

                      Category: device enablement
                      Domain: CWS.BT-Common
                      Origin: internal
                      Upstream-Candidate: blu
                      Signed-off-by: me
                      """,
                     r"bad Upstream-Candidate: blu, allowed:",
                     AOSP_REPO)

    def testAospCorrectDomain(self):
        self.oneTest("""
                      myPatch

                      Category: device enablement
                      Domain: CWS.BT-Common
                      Origin: internal
                      Upstream-Candidate: yes
                      Signed-off-by: me
                      """, None,
                     AOSP_REPO)

    def testAospSeveralParagraphs(self):
        self.oneTest("""
                      myPatch

                      Category: device enablement
                      Domain: CWS.BT-Common

                      Origin: internal
                      Upstream-Candidate: yes
                      Signed-off-by: me
                      """, "meta data should only be part of the last paragraph but there is the line",
                     AOSP_REPO)


def main():
    for tc in TestAospDomains, TestCheckPatch:
        suite = unittest.TestLoader().loadTestsFromTestCase(tc)
        unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    main()
