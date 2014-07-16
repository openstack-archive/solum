#!/bin/bash
# This script tests whether the listed gems were installed correctly

gems=(berkshelf chef rake rubocop foodcritic chefspec test-kitchen kitchen-vagrant)

not_installed=''

for i in "${gems[@]}"
do
  return_value=`gem list $i -i`
  if [ "$return_value" == "false" ]; then
     not_installed+="$i "
  fi
done

if [ -z $not_installed ]; then
    echo "Gems installed correctly"
    exit 0
else
    echo "$not_installed gem(s) not correctly installed"
    exit 1
fi