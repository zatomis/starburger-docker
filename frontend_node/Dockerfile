FROM node:16.16.0-alpine3.16
WORKDIR /webapp
COPY frontend_node/package.json frontend_node/package-lock.json ./
RUN npm install
COPY frontend_node/bundles-src/ ./bundles-src/
#CMD ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

#RUN npm ci --dev
CMD npm ci --dev
CMD ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir /webapp/bundles --public-url="./" &
#CMD ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./" &
#RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
