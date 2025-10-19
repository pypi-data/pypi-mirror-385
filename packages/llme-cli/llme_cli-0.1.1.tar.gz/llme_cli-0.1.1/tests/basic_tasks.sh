#!/bin/bash

. "$(dirname "$0")/utils.sh"

R=PARIS tllme 0.paris "What is the capital of France? Answer in one uppercase word on a single line." "$@"
R=WORK tllme 1.llme "What is the last word of the ./README.md file? Answer in one uppercase word on a single line." "$@"
R=WORK tllme 2.llme README.md "What is the last word of the file? Answer in one uppercase word on a single line." "$@"
R=WORK tllme 3.llme < README.md "What is the last word of the file? Answer in one uppercase word on a single line." "$@"
R="ANSWER:\s*479001600" tllme 4.fact "What is the factorial of 12. Answer with 'ANSWER:' then a single number on a single line." "$@"
