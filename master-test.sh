#!/bin/bash
set -e

# Quick and dirty top level STF master test. This test runs outside the STF
# framework but runs every defined test. This is an interim until a top level
# test that runs within the framework can be developed.

# usage: thisFileName [ stf_test_options ... ]


declare -r PROGRAM=${0##*/}
declare -r PYTHON="/usr/bin/python3"
declare -a TESTS=( )
declare -a TESTOPTS=( )
declare    TestCount=0

info()
{
  printf "%s: " $PROGRAM
  printf "$@"
}
 
error()
{
  info "$@" 1>&2
}

fatal()
{
  error "$@"
  exit 1
}

addTestFile()
{
  local arg="$1"
  if [ -d "$arg" ]; then

    # Run all files in directory
    shopt -s nullglob
    local -ar tests=($arg/*.py)
    for path in ${tests[@]}; do
      local file=${path##*/}
      # skip python ctor
      [ "$file" = "__init__.py" ] && continue
      TESTS+=( "$path" )
    done

  elif [ -e "$arg" ]; then
    TESTS+=( "$arg" )
  else
    fatal "'%s' unknown file type\n" "$arg"
  fi
}

if [ -z "$STF_HOME" ]; then
  export STF_HOME=$(pwd)
  info "setting STF_HOME %s\n" "$STF_HOME"
else
  info "using STF_HOME %s\n" "$STF_HOME"
fi

# parse command line
while [ $# -gt 0 ]; do
  case "$1" in
    -*)
      TESTOPTS+=( "$1" )
      ;;
    *)
      addTestFile "$1"
      ;;
  esac
  shift
done

# Default tests from $STF_HOME/tests
if [ ${#TESTS[@]} -eq 0 ]; then
  tests_dir="$STF_HOME/tests"
  if [ ! -d "$tests_dir" ]; then
    fatal "%s no such directdory\n", "$tests_dir"
  fi
  addTestFile "$tests_dir"
fi
if [ ${#TESTS[@]} -eq 0 ]; then
  fatal "unable to locate test files\n"
fi

cleanup()
{
  printf "\n"
  info "ran %u/%u tests\n" $TestCount ${#TESTS[@]}
  if [ -n "$startTime" ]; then
    endTime=$(date +%s)
    #info "elapsed time: %u s\n" $(expr $endTime - $startTime)
    info "elapsed time: %u s\n" $((  $endTime - $startTime))
  fi
}

startTime=$(date +%s)
trap cleanup EXIT



# main test execution loop
for test in ${TESTS[@]}; do

  # execute each test
  printf "\n\n"
  info "starting test %s ------------------------------------------\n" $test
  $PYTHON $test "${TESTOPTS[@]}"
  status=$?
  info "test %s status: %d\n" $test $status
  ((TestCount++)) || true

done

exit 0

