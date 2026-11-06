# Uses echo and shell control flow available on the target; no printf/sed/awk/grep.
# Selected field lines start with fixed labels, not arbitrary option/escape text.
cluster_fields() {
    in_navigation=0
    while IFS= read -r field_line; do
        # The stock dump indents with spaces. Preserve only selected navigation fields.
        while :; do
            case "$field_line" in ' '*) field_line=${field_line#?};; *) break;; esac
        done
        case "$field_line" in
            'TBT SubInfo:'|'TBT SubInfo2:'|'TBT Info:')
                in_navigation=1; echo "$field_line";;
            'OperationStatus '*|'OperationStatus='*)
                if [ "$in_navigation" = 1 ]; then echo "$field_line"; fi
                in_navigation=0;;
            'Display Type '*|'Side Street '*|'CombisideStreet='*|'Direction '*|'Distance '*|'distance '*|'BarGraph Level='*|'CompassDegree '*|'EstPointType '*)
                if [ "$in_navigation" = 1 ]; then echo "$field_line"; fi;;
            *'Permission Denial:'*) echo CLUSTER_DUMP_PERMISSION_DENIED;;
            *"Can't find service"*) echo CLUSTER_SERVICE_NOT_FOUND;;
        esac
    done
}
