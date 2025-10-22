#!/bin/bash

if [ -z "${KC_DB}" ] || [ "${KC_DB}" = "h2" ]; then
    echo "🏃 Starting Keycloak in development mode with H2..."
    
    # Intentar con import primero, si falla, continuar sin import
    if [ -f "/opt/keycloak/data/import/main-realm.json" ]; then
        echo "📥 Attempting to import realm configuration..."
        if ! /opt/keycloak/bin/kc.sh start-dev --import-realm --log-level=DEBUG --http-port=80; then
            echo "⚠️  Import failed, starting without import..."
            # exec /opt/keycloak/bin/kc.sh start-dev --http-port=80
            /opt/keycloak/bin/kc.sh start-dev --import-realm --log-level=DEBUG --http-port=80 --verbose
        fi
    else
        echo "ℹ️  No realm configuration found, starting clean..."
        exec /opt/keycloak/bin/kc.sh start-dev --http-port=80
    fi
else
    echo "🏭 Starting Keycloak in production mode with external database..."
    echo "🔧 Building configuration for ${KC_DB}..."
    
    if ! /opt/keycloak/bin/kc.sh build --db=${KC_DB}; then
        echo "❌ Failed to build configuration for ${KC_DB}"
        exit 1
    fi
    
    if [ -f "/opt/keycloak/data/import/main-realm.json" ]; then
        echo "📥 Starting with realm import..."
        if ! /opt/keycloak/bin/kc.sh start --import-realm --http-port=80; then
            echo "⚠️  Import failed, starting without import..."  
            exec /opt/keycloak/bin/kc.sh start --http-port=80
        fi
    else
        echo "ℹ️  No realm configuration found, starting clean..."
        exec /opt/keycloak/bin/kc.sh start --http-port=80
    fi
fi