# Use official Python image
FROM python:3.13.2-alpine3.21

# Install system dependencies
RUN apk add --no-cache postgresql-client


#Set working directory
WORKDIR /app

# Copy project files
COPY reqs.txt .

# Install dependencies
RUN pip install --no-cache-dir -r reqs.txt


# Copy application code
COPY ./app .

# Expose port
EXPOSE 8000