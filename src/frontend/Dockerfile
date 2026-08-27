# Step 1: Set base image matching the node-version in GitHub Actions
FROM node:24.14.1-alpine

# Set working directory for the frontend application
WORKDIR /app/src/frontend

# Step 2: Copy lockfile, package manifest and conf files
COPY *.config.* package.json package-lock.json ./

# Clean install dependencies (equivalent to `npm ci`)
RUN npm ci

# Step 3: Copy the rest of the frontend source code
COPY src/ ./src/

# Step 4: Build the application (matches 'Install and build' step)
RUN npm run build

CMD ["npm", "run", "dev"]