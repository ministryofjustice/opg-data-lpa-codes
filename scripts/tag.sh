#!/bin/bash

set -o pipefail

# config
default_semvar_bump=${DEFAULT_BUMP:-minor}
with_v=true
release_branches=main
custom_tag=${CUSTOM_TAG}
source=${SOURCE:-.}
dryrun=${DRY_RUN:-false}
initial_version=${INITIAL_VERSION:-0.0.0}
tag_context=${TAG_CONTEXT:-repo}
suffix=${PRERELEASE_SUFFIX/\//-}
verbose=${VERBOSE:-true}
verbose=${VERBOSE:-true}
# since https://github.blog/2022-04-12-git-security-vulnerability-announced/ runner uses?
git config --global --add safe.directory /github/workspace

cd ${GITHUB_WORKSPACE}/${source}

echo "*** CONFIGURATION ***"
echo -e "\tDEFAULT_BUMP: ${default_semvar_bump}"
echo -e "\tWITH_V: ${with_v}"
echo -e "\tRELEASE_BRANCHES: ${release_branches}"
echo -e "\tCUSTOM_TAG: ${custom_tag}"
echo -e "\tSOURCE: ${source}"
echo -e "\tDRY_RUN: ${dryrun}"
echo -e "\tINITIAL_VERSION: ${initial_version}"
echo -e "\tTAG_CONTEXT: ${tag_context}"
echo -e "\tPRERELEASE_SUFFIX: ${suffix}"
echo -e "\tVERBOSE: ${verbose}"

current_branch=${GITHUB_HEAD_REF:-${GITHUB_REF##*/}}

pre_release="true"
IFS=',' read -ra branch <<< "$release_branches"
for b in "${branch[@]}"; do
   echo "Is $b a match for ${current_branch}"
   if [[ "${current_branch}" =~ $b ]]
   then
       pre_release="false"
   fi
done
echo "pre_release = $pre_release"

# fetch tags
git fetch --tags

tagFmt="^v?[0-9]+\.[0-9]+\.[0-9]+$"
preTagFmt="^v?[0-9]+\.[0-9]+\.[0-9]+(-$suffix\.[0-9]+)?$"

echo "TAG_LIST"
tag=$(semver $(git for-each-ref --sort=-v:refname --format '%(refname:lstrip=2)' | grep -E "$tagFmt") | sort -V | tail -n 1 | grep -E "$tagFmt")
echo $tag
pre_tag=$(semver $(git for-each-ref --sort=-v:refname --format '%(refname:lstrip=2)' | grep -E "$preTagFmt") | sort -V | tail -n 1 | grep -E "$preTagFmt")
echo $pre_tag

if $with_v
then
 ver="v"
else
 ver=""
fi

# if there are none, start tags at INITIAL_VERSION which defaults to 0.0.0
if [ -z "$tag" ]
then
   log=$(git log --pretty='%B')
   tag="$initial_version"
   if [ -z "$pre_tag" ] && $pre_release
   then
     pre_tag="$initial_version"
   fi
else
   log=$(git log $ver$tag..HEAD --pretty='%B')
fi

# get current commit hash for tag
tag_commit=$(git rev-list -n 1 tags/$ver$tag)

# get current commit hash
commit=$(git rev-parse HEAD)

if [ "$tag_commit" == "$commit" ]; then
   echo "No new commits since previous tag. Skipping..."
   echo "tag=$(echo ${tag})" >> $GITHUB_OUTPUT
   exit 0
fi

# echo log if verbose is wanted
if $verbose
then
 echo $log
fi

case "$log" in
   *#major* ) new=$(semver -i major $tag); part="major";;
   *#minor* ) new=$(semver -i minor $tag); part="minor";;
   *#patch* ) new=$(semver -i patch $tag); part="patch";;
   *#none* )
       echo "Default bump was set to none. Skipping..."
       echo "new_tag=$(echo ${tag})" >> $GITHUB_OUTPUT
       echo "tag=$(echo ${tag})" >> $GITHUB_OUTPUT
       exit 0;;
   * )
       if [ "$default_semvar_bump" == "none" ]; then
           echo "Default bump was set to none. Skipping..."
           echo "new_tag=$(echo ${tag})" >> $GITHUB_OUTPUT
           echo "tag=$(echo ${tag})" >> $GITHUB_OUTPUT
           exit 0
       else
           new=$(semver -i "${default_semvar_bump}" $tag)
           part=$default_semvar_bump
       fi
       ;;
esac

if $pre_release
then
   # Already a prerelease available, bump it
   if [[ "$pre_tag" == *"$new"* ]]; then
       echo "Commits exist on branch"
       new=$(semver -i prerelease $pre_tag --preid $suffix)
       part="pre-$part"
   else
       echo "First commit on branch"
       new="$new-$suffix.1"
       part="pre-$part"
   fi
fi

echo $part

# prefix with 'v'
new="$ver$new"

if [ ! -z $custom_tag ]
then
   new="$custom_tag"
fi

if $pre_release
then
   echo -e "Bumping tag ${pre_tag}. \n\tNew tag ${new}"
else
   echo -e "Bumping tag ${tag}. \n\tNew tag ${new}"
fi

# set outputs
echo "new_tag=$(echo ${new})" >> $GITHUB_OUTPUT
echo "part=$(echo ${part})" >> $GITHUB_OUTPUT

# use dry run to determine the next tag
if $dryrun
then
   echo "tag=$(echo ${tag})"
   exit 0
fi

echo "tag=$(echo ${new})" >> $GITHUB_OUTPUT

# create local git tag
git tag $new

# push new tag ref to github
dt=$(date '+%Y-%m-%dT%H:%M:%SZ')
full_name=$GITHUB_REPOSITORY
git_refs_url=$(jq .repository.git_refs_url $GITHUB_EVENT_PATH | tr -d '"' | sed 's/{\/sha}//g')

echo "$dt: **pushing tag $new to repo $full_name"

git_refs_response=$(
curl -s -X POST $git_refs_url \
-H "Authorization: token $GITHUB_TOKEN" \
-d @- << EOF
{
 "ref": "refs/tags/$new",
 "sha": "$commit"
}
EOF
)

git_ref_posted=$( echo "${git_refs_response}" | jq .ref | tr -d '"' )

echo "::debug::${git_refs_response}"
if [ "${git_ref_posted}" = "refs/tags/${new}" ]; then
 exit 0
else
 echo "::error::Tag was not created properly."
 exit 1
fi
