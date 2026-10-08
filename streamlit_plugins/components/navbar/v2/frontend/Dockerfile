FROM node:24-alpine3.24

WORKDIR /frontend

COPY package.json package-lock.json ./
COPY tsconfig.json .
COPY vite.config.ts .

RUN npm ci

CMD ["npm", "run", "dev"]