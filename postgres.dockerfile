# postgres/Dockerfile
FROM postgres:latest

# Set environment variables
ENV POSTGRES_USER=user
ENV POSTGRES_PASSWORD=pass
ENV POSTGRES_DB=umls_db

# Copy initialization SQL scripts (optional)
# COPY init.sql /docker-entrypoint-initdb.d/

EXPOSE 5432