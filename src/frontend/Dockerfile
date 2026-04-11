FROM node:20-alpine AS builder

WORKDIR /app

#COPY package*.json ./
COPY . ./

#Generate package-lock.json
RUN npm install

RUN npm install --save-dev @tsconfig/svelte typescript svelte-preprocess svelte-check

RUN npm ci

RUN npx svelte-kit sync

RUN npx svelte-check

#RUN npm create vite@latest myapp -- --template svelte-ts

RUN npm run build

FROM nginx:alpine
#FROM alpine

COPY --from=builder /app/build /usr/share/nginx/html
#COPY --from=builder /app /mnt
COPY nginx.conf /etc/nginx/conf.d/default.conf
#CMD ["/bin/sh"]

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
