for line in `find . -iname *.sxw`; do python openerp_sxw2rml.py $line > ${line%.*}.rml; done
