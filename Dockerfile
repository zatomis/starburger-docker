FROM node:16.16.0-alpine3.16
WORKDIR /webapp
COPY frontend_node/package.json frontend_node/package-lock.json ./
RUN npm install
COPY frontend_node/bundles-src/ ./bundles-src/
RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
