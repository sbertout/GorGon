#!/usr/bin/env bash
echo kl compiling !:1; rm -f /tmp/klc!:1.kl ; echo 'require !:1 ; operator entry ( ) {}' >> /tmp/klc!:1.kl ; kl /tmp/klc!:1.kl
