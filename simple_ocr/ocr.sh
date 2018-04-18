#!/bin/sh

# requirements
# tesseract-ocr tesseract-ocr-rus imagemagick libreoffice-writer openjdk-8-jre

file_name="${1}"
txt_file_name=`echo "${file_name}" | sed -e 's/\..*$//g'`
convert ${3} ${4} "${file_name}" -depth 8 -strip -background white -alpha off "${txt_file_name}.tiff"
tesseract -l rus "${txt_file_name}.tiff" "${txt_file_name}"
libreoffice --invisible --headless --convert-to docx --outdir "${2}" "${txt_file_name}.txt"