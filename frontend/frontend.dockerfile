FROM node:22

WORKDIR /app

RUN npm install -g @angular/cli@20

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 4200

CMD ["ng", "serve", "--port", "4200", "--host", "0.0.0.0"]
