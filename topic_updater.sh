for topic in 01org aosp art audio autodetect boot-devel camera comms graphics-gen sensors system-integration telephony
do
    mkdir -p topic/$topic
    repo manifest -o topic/$topic/master
    sed -i "s|android/l/mr1/r1|abt/topic/gmin/l-dev/mr1/$topic/master|g" topic/$topic/master
    sed -i "s|android/l/mr1/master|abt/topic/gmin/l-dev/mr1/$topic/master|g" topic/$topic/master
    sed -i "s|name=\"manifests\" revision=\"abt/topic/gmin/l-dev/mr1/$topic/master|name\"manifests\" revision=\"android/l/mr1/master\"|" topic/$topic/master
done

for topic in scale bxt
do
    mkdir -p topic/staging/$topic
    repo manifest -o topic/staging/$topic/master
    sed -i "s|android/l/mr1/r1|abt/topic/gmin/staging/$topic/master|g" topic/staging/$topic/master    
    sed -i "s|android/l/mr1/master|abt/topic/gmin/staging/$topic/master|g" topic/staging/$topic/master
    sed -i "s|name=\"manifests\" revision=\"abt/topic/gmin/staging/$topic/master|name=\"manifests\" revision=\"android/l/mr1/master\"|" topic/staging/$topic/master
done
