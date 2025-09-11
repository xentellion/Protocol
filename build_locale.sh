#!/bin/bash
find . -name "*.py" >POTFILES
xgettext --from-code=utf-8 --files-from POTFILES -o ./locales/protocol.pot
sed -i 's/charset=CHARSET/charset=UTF-8/g' ./locales/protocol.pot
for dir in ./locales/*; do
    if [ -d "$dir" ]; then
        if [ -e "${dir}/LC_MESSAGES/protocol.po" ]; then
            msgmerge "${dir}/LC_MESSAGES/protocol.po" ./locales/protocol.pot -o "${dir}/LC_MESSAGES/protocol.po"
        else
            cp ./locales/protocol.pot "${dir}/LC_MESSAGES/protocol.po"
        fi
        msgfmt -o "${dir}/LC_MESSAGES/protocol.mo" "${dir}/LC_MESSAGES/protocol.po"
    fi
done
