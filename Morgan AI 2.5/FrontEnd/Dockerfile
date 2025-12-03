# Build stage
FROM node:slim AS build
WORKDIR /app
COPY package*.json ./
# Use npm ci when a lockfile exists; otherwise fall back to npm install
RUN if [ -f package-lock.json ]; then npm ci; else npm install --no-audit --no-fund; fi
COPY . .
# Build using the root package.json script (config points to FrontEnd/vite.config.js)
RUN npm run build

# Serve stage
FROM nginx:alpine
COPY --from=build /app/FrontEnd/dist /usr/share/nginx/html
COPY FrontEnd/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]