# Install rclone for Google Cloud Storage uploads
curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip
unzip rclone-current-linux-amd64.zip
export PATH=$(ls -d rclone-v*):$PATH

# Decrypt key for Google Cloud Storage deployment
openssl aes-256-cbc \
  -K $encrypted_c4ed8e889cf2_key \
  -iv $encrypted_c4ed8e889cf2_iv \
  -in ci/item-historical-database-d0b06349d741.json.enc \
  -out ci/item-historical-database-d0b06349d741.json \
  -d
