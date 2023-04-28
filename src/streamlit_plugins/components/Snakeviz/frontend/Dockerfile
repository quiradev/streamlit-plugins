FROM node:16-alpine3.17
RUN apk add git

WORKDIR /frontend

COPY package.json .
COPY tsconfig.json .

RUN npm install

RUN mkdir -p declarations/apache-arrow/
RUN cp -R node_modules/apache-arrow/* declarations/apache-arrow/
RUN find declarations/apache-arrow ! -name "*d.ts" -and ! -name "package.json" -type f -delete
RUN echo -e "// @ts-nocheck\n$(cat declarations/apache-arrow/column.d.ts)" > declarations/apache-arrow/column.d.ts
RUN echo -e "// @ts-nocheck\n$(cat declarations/apache-arrow/ipc/reader.d.ts)" > declarations/apache-arrow/ipc/reader.d.ts
RUN echo -e "// @ts-nocheck\n$(cat declarations/apache-arrow/recordbatch.d.ts)" > declarations/apache-arrow/recordbatch.d.ts

CMD ["npm", "run", "start"]