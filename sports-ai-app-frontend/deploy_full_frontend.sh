#!/bin/bash
set -e

### ==========================================================
### CONFIG DEL USUARIO
### ==========================================================
AWS_REGION="us-east-1"
BUCKET_NAME="sports-ai-app-frontend-prod"
BUILD_DIR="dist"

echo "=========================================================="
echo " 🚀 Deploy Full Auto: S3 + CloudFront (Vite Frontend)"
echo "=========================================================="
echo ""

### ==========================================================
### 1. Construir Vite
### ==========================================================
echo "📦 Construyendo proyecto con Vite..."
npm install
npm run build

if [ ! -d "$BUILD_DIR" ]; then
  echo "❌ ERROR: No existe la carpeta dist/. Build fallida."
  exit 1
fi

echo "✔ Build completada."
echo ""

### ==========================================================
### 2. Crear Bucket S3 si no existe (FIX for us-east-1)
### ==========================================================
echo "🪣 Validando bucket S3..."

BUCKET_EXISTS=$(aws s3api head-bucket --bucket $BUCKET_NAME 2>&1 || true)

if [[ $BUCKET_EXISTS == *"Not Found"* ]] || [[ $BUCKET_EXISTS == *"404"* ]]; then
    echo "🔧 Creando bucket: $BUCKET_NAME ..."

    if [ "$AWS_REGION" = "us-east-1" ]; then
        # us-east-1 special case: MUST NOT specify LocationConstraint
        aws s3api create-bucket \
            --bucket $BUCKET_NAME \
            --region us-east-1
    else
        aws s3api create-bucket \
            --bucket $BUCKET_NAME \
            --region $AWS_REGION \
            --create-bucket-configuration LocationConstraint=$AWS_REGION
    fi

    echo "✔ Bucket creado."
else
    echo "✔ Bucket ya existe."
fi


### ==========================================================
### 3. Habilitar hosting estático
### ==========================================================
echo "🌐 Configurando bucket para Static Website Hosting..."

aws s3 website s3://$BUCKET_NAME/ \
  --index-document index.html \
  --error-document index.html

echo "✔ Hosting estático habilitado."
echo ""

### ==========================================================
### 4. Hacer objetos públicos
### ==========================================================
echo "👮 Configurando política pública del bucket..."

echo "🔓 Desbloqueando Public Bucket Policies..."

aws s3api put-public-access-block \
  --bucket $BUCKET_NAME \
  --public-access-block-configuration '{
    "BlockPublicAcls": false,
    "IgnorePublicAcls": false,
    "BlockPublicPolicy": false,
    "RestrictPublicBuckets": false
  }'

echo "✔ Bucket ahora permite políticas públicas (seguro pero accesible)."


aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy "{
  \"Version\":\"2012-10-17\",
  \"Statement\":[
    {
      \"Sid\":\"PublicRead\",
      \"Effect\":\"Allow\",
      \"Principal\":\"*\",
      \"Action\":\"s3:GetObject\",
      \"Resource\":\"arn:aws:s3:::$BUCKET_NAME/*\"
    }
  ]
}"

echo "✔ Bucket ahora es público."
echo ""

### ==========================================================
### 5. Subir archivos /dist al bucket
### ==========================================================
echo "⬆️ Subiendo frontend al bucket..."

aws s3 sync $BUILD_DIR s3://$BUCKET_NAME --delete

echo "✔ Archivos sincronizados."
echo ""

### ==========================================================
### 6. Crear distribución CloudFront automáticamente
### ==========================================================
echo "🛰  Creando distribución CloudFront..."

ORIGIN_DOMAIN="$BUCKET_NAME.s3-website-$AWS_REGION.amazonaws.com"

CF_CONFIG=$(cat <<EOF
{
  "CallerReference": "deploy-$(date +%s)",
  "Comment": "Frontend MMA AI",
  "Enabled": true,
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3Origin",
        "DomainName": "$ORIGIN_DOMAIN",
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "http-only"
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3Origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"]
    },
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": { "Forward": "none" }
    },
    "MinTTL": 0,
    "DefaultTTL": 86400,
    "MaxTTL": 31536000
  },
  "CustomErrorResponses": {
    "Quantity": 1,
    "Items": [
      {
        "ErrorCode": 404,
        "ResponsePagePath": "/index.html",
        "ResponseCode": "200",
        "ErrorCachingMinTTL": 0
      }
    ]
  }
}
EOF
)


CF_OUTPUT=$(aws cloudfront create-distribution --distribution-config "$CF_CONFIG")
DISTRIBUTION_ID=$(echo $CF_OUTPUT | jq -r '.Distribution.Id')
CF_DOMAIN=$(echo $CF_OUTPUT | jq -r '.Distribution.DomainName')

echo "✔ CloudFront creado:"
echo "   ID: $DISTRIBUTION_ID"
echo "   URL: https://$CF_DOMAIN"
echo ""

### ==========================================================
### 7. Mostrar resultado final
### ==========================================================
echo "=========================================================="
echo " 🎉 DEPLOY COMPLETADO"
echo "----------------------------------------------------------"
echo " 🌍 URL de tu sitio:"
echo " 👉 https://$CF_DOMAIN"
echo ""
echo " 🪣 S3 Hosting directo (no recomendado):"
echo " 👉 http://$ORIGIN_DOMAIN"
echo "=========================================================="
