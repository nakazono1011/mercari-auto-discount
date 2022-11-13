FROM node:16 AS build
ADD . /app
WORKDIR /app
RUN yarn install --production=false
RUN yarn build

FROM gcr.io/distroless/nodejs:16
WORKDIR /app
COPY --from=build /app/next.config.js ./
COPY --from=build /app/public ./public
COPY --from=build /app/package.json ./package.json
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/.next/standalone ./

CMD ["server.js"]