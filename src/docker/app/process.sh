#/bin/bash
BUCKET_NAME_SOURCE=$1
OBJECT_KEY=$2
BUCKET_NAME_DESTINATION=$3

echo "[DEBUG] Source Bucket = "$BUCKET_NAME_SOURCE
echo "[DEBUG] Source Object = "$OBJECT_KEY
echo "[DEBUG] Destination Bucket = "$BUCKET_NAME_DESTINATION

echo "[INFO] Copying file from source bucket"
aws s3 cp s3://$BUCKET_NAME_SOURCE/$OBJECT_KEY /tmp/$OBJECT_KEY
echo "[INFO] File copied"

echo "[INFO] Processing file"
aws s3 cp /tmp/$OBJECT_KEY s3://$BUCKET_NAME_DESTINATION/processed-$OBJECT_KEY
echo "[INFO] File processed"
