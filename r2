<?xml version="1.0" encoding="UTF-8"?>
<manifest>

  <remote name="origin"
          fetch="ssh://android-mirror.devtools.intel.com"
          review="https://android.intel.com" />

  <remote  name="aosp"
           fetch="https://android.googlesource.com" />
  <default revision="refs/tags/android-9.0.0_r45"
           remote="aosp"
           sync-c="true"
           sync-j="4" />

  <remote  name="github"
           fetch="https://github.com/projectceladon/" />


  <include name="include/aosp_vanilla.xml" />
  <include name="include/remove_vanilla.xml" />
  <include name="include/bsp-celadon.xml" />
  <include name="include/bsp-private-celadon.xml"/>
  <include name="include/manifest-celadon.xml" />

</manifest>
