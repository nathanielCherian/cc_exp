#!/bin/bash

# Check if any arguments are passed
if [ $# -eq 0 ]; then
  echo "This script converts .pcap files to a more parse-able .csv format."
  echo "To convert X.pcap to X.csv, run './pcap2csv.sh X [Y Z ...]' "
  exit
fi

# Loop over each argument passed to the script
for file in "$@"; do
  echo -e "[Converting $file to .csv format]"

  # Create separate traces for TCP and UDP traffic
  tshark -r "$file" -T fields -o "gui.column.format:\"Time\",\"%Aut\"" \
    -e _ws.col.Time -e frame.time_relative -e tcp.time_relative -e frame.number \
    -e frame.len -e ip.src -e tcp.srcport -e ip.dst -e tcp.dstport -e tcp.len \
    -e tcp.seq -e tcp.ack -E header=y -E separator=, -E quote=d -E occurrence=f \
    > "${file%.pcap}-tcp.csv"

  echo "Conversion for $file completed."
done

