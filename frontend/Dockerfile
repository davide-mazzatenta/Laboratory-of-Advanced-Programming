# Stage 1: Build the React app
FROM node:20-alpine as build

WORKDIR /app

# Add build argument for the API URL
ARG REACT_APP_API_URL

# Set the environment variable for the build process
ENV REACT_APP_API_URL=$REACT_APP_API_URL

# Copy package files
COPY package*.json ./
RUN npm install 

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy build output
COPY --from=build /app/build /usr/share/nginx/html

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --spider -q http://localhost:80/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]