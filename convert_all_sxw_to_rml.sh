for line in `find . -iname *.sxw`; do 
    echo "Converting $line      >       ${line%.*}.rml"
    python openerp_sxw2rml.py $line > ${line%.*}.rml
done
