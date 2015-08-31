#!/usr/bin/env python
import unittest
import yaml
import os
from check_manifest_xml import CheckManifestSrcPath

class DomainYamlConfigCheck(object):

    @staticmethod
    def checkProjectDomainToPathCoverage(sourceDomain):
        """check if path of repo defined in all xml file have a domain associated"""
        errors = []
        project = CheckManifestSrcPath()
        for path_in_xml_manifest_file,path_found_in_file in project.project_path_list:
             path_have_domain = False
             for (domain_from_source_to_domain, path_from_source_to_domain) in sourceDomain.iteritems():
                if path_in_xml_manifest_file in path_from_source_to_domain:
                    path_have_domain = True
                    break
             if not path_have_domain:
                    errors.extend(["{} {}".format(path_found_in_file.ljust(30),path_in_xml_manifest_file.ljust(70))])
        if errors:
            return list(set(errors))
        else:
            print "all path have domain associated"

    @staticmethod
    def checkProjectDomainConfiguration(sourceToDomainCategory, selectDomain, domainName):
        errors = []
        multiple = [(p, selectDomain(primaries, secondaries))
                    for (p, (primaries, secondaries)) in sourceToDomainCategory.iteritems()
                    if len(selectDomain(primaries, secondaries)) > 1]
        if multiple:
            for (p, domains) in multiple:
                errors.extend(["{} is set to the same {} domain:"
                               " {} multiple times".format(p, domainName, duplicateDomain)
                               for duplicateDomain in set([d for d in domains
                                                           if domains.count(d) > 1])])
                multipleDomain = set(domains)
                if len(multipleDomain) > 1:
                    errors.extend(["{} has multiple {} domains: {}".format(p, domainName,
                                                                           ", ".join(multipleDomain))])
        return errors

    @staticmethod
    def checkNoMultipleDomains(sourceToDomain):
        errors = []
        sourceToDomainCategory = {}
        for domain, path_list in sourceToDomain.iteritems():
            for p in path_list:
                isSecondaryDomain = p.startswith('^')
                p = p.replace('^', '')
                relatedPrimary, relatedSecondary = sourceToDomainCategory.setdefault(p, ([], []))
                if isSecondaryDomain:
                    relatedSecondary.append(domain)
                else:
                    relatedPrimary.append(domain)
        errors.extend(DomainYamlConfigCheck.checkProjectDomainConfiguration(sourceToDomainCategory,
                                                                            lambda p, s: p,
                                                                            "primary"))
        errors.extend(DomainYamlConfigCheck.checkProjectDomainConfiguration(sourceToDomainCategory,
                                                                            lambda p, s: s,
                                                                            "secondary"))
        duplicatedPrimarySecondary = [(p, set(primaries) & set(secondaries))
                                      for p, (primaries, secondaries) in
                                      sourceToDomainCategory.iteritems()]
        duplicatedPrimarySecondary = [(p, dup) for p, dup in duplicatedPrimarySecondary
                                      if dup]
        if duplicatedPrimarySecondary:
            errors.extend(["{} is set as primary and secondary domain for {}".format(p,
                                                                                     ", ".join(dupDomains))
                           for p, dupDomains in duplicatedPrimarySecondary])
        return sourceToDomainCategory, errors

class TestTestToDomainYamlConfig(unittest.TestCase):
    def testCheckMultipleDomainNominal(self):
        sourceToDomain = {'d1': ['p1', 'p2', '^p3']}
        cat, errors = DomainYamlConfigCheck.checkNoMultipleDomains(sourceToDomain)
        self.assertEquals(cat, {'p1': (['d1'], []),
                                'p2': (['d1'], []),
                                'p3': ([], ['d1'])})
        self.assertEquals(errors, [])

    def testCheckMultiplePrimaryDomain(self):
        sourceToDomain = {'d1': ['p1', '^p3'],
                          'd2': ['p1']}
        _, errors = DomainYamlConfigCheck.checkNoMultipleDomains(sourceToDomain)
        self.assertEquals(errors, ['p1 has multiple primary domains: d2, d1'])

    def testCheckMultipleSecondaryDomain(self):
        sourceToDomain = {'d1': ['^p1', '^p3'],
                          'd2': ['^p1']}
        _, errors = DomainYamlConfigCheck.checkNoMultipleDomains(sourceToDomain)
        self.assertEquals(errors, ['p1 has multiple secondary domains: d2, d1'])

    def testCheckSamePrimaryDomainPutTwice(self):
        sourceToDomain = {'d1': ['p1', 'p1'],
                          'd2': ['p2']}
        _, errors = DomainYamlConfigCheck.checkNoMultipleDomains(sourceToDomain)
        self.assertEquals(errors, ['p1 is set to the same primary domain: d1 multiple times'])

    def testCheckSameSecondaryDomainPutTwice(self):
        sourceToDomain = {'d1': ['^p1', '^p1'],
                          'd2': ['p2']}
        _, errors = DomainYamlConfigCheck.checkNoMultipleDomains(sourceToDomain)
        self.assertEquals(errors, ['p1 is set to the same secondary domain: d1 multiple times'])

    def testCheckSamePrimaryDomainSecondaryDomainMess(self):
        sourceToDomain = {'d1': ['p1', '^p1'],
                          'd2': ['p2']}
        _, errors = DomainYamlConfigCheck.checkNoMultipleDomains(sourceToDomain)
        self.assertEquals(errors, ['p1 is set as primary and secondary domain for d1'])

    def testCheckMultiplDomainMix(self):
        sourceToDomain = {'d1': ['p1', '^p1', 'p2'],
                          'd2': ['p2', '^p2', 'p1']}
        _, errors = DomainYamlConfigCheck.checkNoMultipleDomains(sourceToDomain)
        self.assertEquals(errors, ['p2 has multiple primary domains: d2, d1',
                                   'p1 has multiple primary domains: d2, d1',
                                   'p2 is set as primary and secondary domain for d2',
                                   'p1 is set as primary and secondary domain for d1'])

class TestToDomainYamlConfig(DomainYamlConfigCheck, unittest.TestCase):
    SOURCE_TO_DOMAIN = "source-to-domain.yaml"
    SOURCE_TO_DOMAIN_KW = "source-to-domain-kw.yaml"
    REVIEWERS_TO_DOMAIN = "reviewers-to-domain.yaml"
    VERIFIERS_TO_DOMAIN = "verifiers-to-domain.yaml"
    LEADER_TO_DOMAIN = "leader-to-domain.yaml"

    def toYaml(self, yamlFile):
        path = os.path.join(os.path.dirname(__file__), "..", yamlFile)
        r = None
        with open(path, 'r') as f:
            r = yaml.load(f.read())
        return r

    def testParseToDomainConfig(self):
        toDomainConfigFiles = {k: self.toYaml(k)
                               for k in [self.SOURCE_TO_DOMAIN,
                                         self.REVIEWERS_TO_DOMAIN,
                                         self.VERIFIERS_TO_DOMAIN,
                                         self.LEADER_TO_DOMAIN]}
        sourceToDomainCategory, errors = self.checkNoMultipleDomains(toDomainConfigFiles[self.SOURCE_TO_DOMAIN])
        if errors:
            errors = ["{} :".format(self.SOURCE_TO_DOMAIN)] + errors
        allDomains = set(sum([x[0] + x[1] for x in sourceToDomainCategory.values()], []))
        for domainToUserName in [self.REVIEWERS_TO_DOMAIN,
                                 self.VERIFIERS_TO_DOMAIN,
                                 self.LEADER_TO_DOMAIN]:
            domainToUser = toDomainConfigFiles[domainToUserName]
            for (k, v) in domainToUser.iteritems():
                if v is None:
                    errors.extend(["No domain value for {} in {}".format(k, domainToUserName)])

            if not errors:
                notDefinedDomains = set(sum(domainToUser.values(), [])) - allDomains
                if notDefinedDomains:
                    errors.extend(["{}: ".format(domainToUserName)] +
                                  ["domain {} is not defined in {}".format(x, self.SOURCE_TO_DOMAIN)
                                   for x in notDefinedDomains])
        if errors:
            raise ValueError("\n".join(sorted(errors)))

    def testPathWithoutDomain(self):
        for sourceToDomain in [self.SOURCE_TO_DOMAIN,
                               self.SOURCE_TO_DOMAIN_KW]:
            print ("\n-------------------------------------------- Test Domain coverage for {}".format(sourceToDomain))
            errors = DomainYamlConfigCheck.checkProjectDomainToPathCoverage(self.toYaml(sourceToDomain))
            errors.sort()
            if errors:
               print "\nNo domain attached for the following path:"
               for path_wo_domain in errors:
                  print path_wo_domain
        print "\n-------------------------------------------- Test Domain coverage end"

def main():
    for tc in {TestTestToDomainYamlConfig, TestToDomainYamlConfig}:
        suite = unittest.TestLoader().loadTestsFromTestCase(tc)
        unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    main()
