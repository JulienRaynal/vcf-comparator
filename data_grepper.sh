$(echo "" > oscur.txt)
FILENAMES=()
COUNTER=0
# For each VCF file in the folder: save the VCF file name
for FILE in ./*.vcf; do 
	FILENAMES[${#FILENAMES[@]}]=$FILE;
done;
IFS=$'\n' SORTED=($(sort <<<"${FILENAMES[*]}")); unset IFS;

# For each VCF file name
for ((idx=0; idx<=${#SORTED[@]} - 1; ++idx)); do
	echo "$idx" "${SORTED[idx]}"
	# Get the data in the file that we are interested in
	ID="$(cat ${SORTED[idx]}  | grep -v "^#" | cut -d$'\t'  -f2)"
	REF=$(cat ${SORTED[idx]}  | grep -v "^#" | cut -d$'\t'  -f4)
	ALT=$(cat ${SORTED[idx]}  | grep -v "^#" | cut -d$'\t'  -f5)
	SVTYPE=$(grep -v "^#" ${SORTED[idx]} | grep -oE "SVTYPE=[A-Z]*")
	SVLEN=$(grep -v "^#" ${SORTED[idx]} | grep -oE "SVLEN=[0-9-]*")
	END=$(grep -v "^#" ${SORTED[idx]} | grep -oE "END=[0-9]*")
	AF=$(grep -v "^#" ${SORTED[idx]} | grep -oE "AF=[0-9.]*")
	
	DR=$(grep -v "^#" ${SORTED[idx]} | cut -d$'\t' -f10 | cut -d ':' -f3) 
	DV=$(grep -v "^#" ${SORTED[idx]} | cut -d$'\t' -f10 | cut -d ':' -f4) 
 
	# Get the passages and the cultures
	PASSAGE=$(echo ${SORTED[idx]} | grep -oE P[0-9].)
	CULTURE=$(echo ${SORTED[idx]} | grep -oE C[0-9]*)

	# Append to a file all the data we have saved
	FILE=$(paste <(printf %s "$ID") <(printf %s "$REF") <(printf %s "$ALT") <(printf %s "$SVTYPE") <(printf %s "$SVLEN") <(printf %s "$END") <(printf %s "$AF") <(printf %s "$PASSAGE") <(printf %s "$CULTURE") <(printf %s "$DR") <(printf %s "$DV"))
	$(echo "$FILE" >> oscur.txt)
	
done

