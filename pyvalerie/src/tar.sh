#/bin/bash
mkdir -p hdd/valerie
mkdir -p hdd/valerie/cache
mkdir -p hdd/valerie/media
mkdir -p hdd/valerie/episodes
cp valerie.conf hdd/valerie
cp paths.conf hdd/valerie

mkdir -p usr/lib/enigma2/python/Plugins/Extensions/ProjectValerieSync
cp *.py usr/lib/enigma2/python/Plugins/Extensions/ProjectValerieSync/

tar czf ProjectValerieSync.tar.gz hdd usr

rm -rf hdd
rm -rf usr
