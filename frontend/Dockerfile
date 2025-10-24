FROM node:18-alpine

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj package.json i package-lock.json (jeśli istnieje)
COPY package*.json ./

# Zainstaluj zależności
RUN npm ci --only=production

# Skopiuj kod aplikacji
COPY . .

# Zbuduj aplikację
RUN npm run build

# Expose port
EXPOSE 3000

# Ustaw zmienne środowiskowe
ENV NODE_ENV=production

# Komenda startowa
CMD ["npm", "run", "preview"]