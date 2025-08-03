FROM mcr.microsoft.com/playwright/python:v1.40.0

# Install cron
RUN apt-get update && apt-get install -y cron

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script
COPY plex-to-letterboxd.py .

# Install Playwright browsers
RUN playwright install chromium

# Create the cron job file
RUN echo "0 0 * * * cd /app && python /app/plex-to-letterboxd.py >> /var/log/cron.log 2>&1" > /etc/cron.d/plex-letterboxd-cron
RUN chmod 0644 /etc/cron.d/plex-letterboxd-cron

# Apply the cron job
RUN crontab /etc/cron.d/plex-letterboxd-cron

# Create the log file
RUN touch /var/log/cron.log

# Create startup script
RUN echo '#!/bin/bash\n\
if [ "$START_NOW" = "true" ]; then\n\
    echo "Running script immediately..."\n\
    python /app/plex-to-letterboxd.py\n\
fi\n\
cron\n\
tail -f /var/log/cron.log' > /app/startup.sh

RUN chmod +x /app/startup.sh

CMD ["/app/startup.sh"]