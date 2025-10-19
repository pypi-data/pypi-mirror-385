FROM postgres:15.3
ENV POSTGRES_USER=event_user
ENV POSTGRES_PASSWORD=event_pass
ENV POSTGRES_DB=event_store_db

RUN mkdir -p /docker-entrypoint-initdb.d/
COPY init.sql /docker-entrypoint-initdb.d/
EXPOSE 5432