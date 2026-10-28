# Use lightweight Nginx Alpine Linux image to serve static files
FROM nginx:alpine

# Copy HTML landing page to Nginx web root directory
COPY index.html /usr/share/nginx/html/index.html

# Copy CSS styling file to Nginx web root directory
COPY style.css /usr/share/nginx/html/style.css

# Copy JavaScript frontend logic file to Nginx web root directory
COPY app.js /usr/share/nginx/html/app.js

# Copy menu food images folder into Nginx web directory
COPY assets/ /usr/share/nginx/html/assets/

# Expose standard HTTP web port 80
EXPOSE 80

# Run Nginx in foreground mode to keep the container running
CMD ["nginx", "-g", "daemon off;"]