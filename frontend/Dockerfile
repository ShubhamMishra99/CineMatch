# Build Stage
FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Production Stage (serve with NGINX)
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration if needed, or use default
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
