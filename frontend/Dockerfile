FROM node:18

WORKDIR /app

COPY . /app

RUN npm install
RUN npm run build

# Exponer el puerto en el que correrá el servidor de SvelteKit
EXPOSE 3000

# Comando para iniciar el servidor
CMD ["node", "build"]
