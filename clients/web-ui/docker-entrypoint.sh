#!/bin/sh

# Environment variable substitution for runtime configuration
if [ -n "$REACT_APP_API_URL" ]; then
    # Replace API URL in built files
    find /usr/share/nginx/html -name "*.js" -exec sed -i "s|http://localhost:8002|$REACT_APP_API_URL|g" {} \;
fi

# Execute the original command
exec "$@"