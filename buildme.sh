#!/bin/bash
set -e

echo Updating changelog
export version=$(date "+%Y%m%d.%H%M")
gbp dch --debian-tag="%(version)s" --new-version=$version --debian-branch master --release

echo Updating version in setup.py
sed -i -- "s/version='.*'/version='$version'/" setup.py

echo Committing changelog and setup.py
git add debian/changelog setup.py
git commit -m "Annotate changelog, update version"

echo Tagging and pushing tags
git tag $version
git push
git push --tags

echo Building package
gbp buildpackage --git-pbuilder --git-dist=wheezy --git-arch=amd64 --git-ignore-branch

# build for pypi
python setup.py sdist bdist_wheel

echo -e "Now to dput run:\ndput --unchecked -c /etc/byte.cf wheezy ../CHANGESFILE"
echo -e "Or to upload to PyPI run:\ntwine upload -r pypi dist/*"
