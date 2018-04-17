#!/bin/sh

# requirements
# tesseract-ocr tesseract-ocr-rus imagemagick libreoffice-writer

file_name="${1}"
txt_file_name=`echo "${file_name}" | sed -e 's/\..*$//g'`
convert -density 300 "${file_name}" -depth 8 -strip -background white -alpha off out.tiff
tesseract -l rus out.tiff "${txt_file_name}"
libreoffice --invisible --headless --convert-to docx "${txt_file_name}.txt"