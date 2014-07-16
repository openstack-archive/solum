#!/bin/bash -x
# This script tests whether golang tools were correctly installed or not

return_value=`go run ./hello.go`

if [ "$return_value" == "hello world" ]; then
    echo "Go tools correctly installed."
    exit 0
else
    echo "Go tools not correctly installed."
    echo "Expected:hello world; Got: $return_value"
    exit 1
fi
