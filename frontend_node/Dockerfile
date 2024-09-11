FROM node:16.16.0
WORKDIR /webapp
COPY frontend_node/package.json frontend_node/package-lock.json ./
RUN npm install
COPY frontend_node/bundles-src/ ./bundles-src/
RUN npm ci --dev
COPY . ./
EXPOSE 3000
