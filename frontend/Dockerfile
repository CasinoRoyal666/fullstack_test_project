FROM node:22.14.0
WORKDIR /app
COPY package*.json ./
RUN npm ci  
COPY . .
EXPOSE 3000
CMD ["sh", "-c", "npm run build && npm start"]