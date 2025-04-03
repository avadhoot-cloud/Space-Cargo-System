FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Remove production build step - causing issues
# RUN npm run build

EXPOSE 3000

# Use development mode
ENV NODE_ENV=development
CMD ["npm", "start"]