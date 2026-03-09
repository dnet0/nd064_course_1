# Use a Python base image in version 3.8
FROM python:3.8
LABEL maintainer="Johan"

COPY ./techtrends /app
WORKDIR /app

# Install packages defined in the requirements.txt file
RUN pip install -r requirements.txt
# Initialized the DB
RUN python init_db.py

# Expose the application port 3111
EXPOSE 3111

# The application should execute at the container start
CMD [ "python", "app.py" ]