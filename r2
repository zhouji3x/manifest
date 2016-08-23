<?xml version="1.0" encoding="UTF-8"?>
<manifest>

  <notice>One_Android_Ring='2'</notice>

  <default revision="android/n/mr0/r2"
           remote="origin"
           sync-c="true"
           sync-j="5" />

  <include name="rbase.xml"/>
  <project name="manifests" path="manifests"  groups="embargoed" revision="android/master">
    <annotation name="readonly" value="true" />
  </project>

  <!-- The project below is used for google_diff that needs to be different
  between master and master_car. For master, it will continue pointing to android/master branch -->
  <project path="vendor/intel/utils" name="a/bsp/vendor/intel/PRIVATE/utils" groups="bsp-priv,embargoed" revision="android/master">
      <annotation name="g_external" value="no"/>
      <annotation name="all_external" value="no"/>
      <annotation name="bxt_rvp_external" value="no"/>
  </project>
</manifest>
