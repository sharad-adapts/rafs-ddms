ARG python_version=3.11
FROM mcr.microsoft.com/mirror/docker/library/python:${python_version}-slim
ARG python_version
COPY requirements.txt /app/requirements.txt
RUN apt update && apt install -y build-essential cmake ca-certificates lsb-release wget \
      && wget https://apache.jfrog.io/artifactory/arrow/$(lsb_release --id --short | tr 'A-Z' 'a-z')/apache-arrow-apt-source-latest-$(lsb_release --codename --short).deb -O /tmp/apache-arrow.deb \
      && apt -y install /tmp/apache-arrow.deb && apt update \
      && apt install -y -V libarrow-dev \
      && pip install --upgrade pip \
      && pip install --no-cache-dir -r /app/requirements.txt \
      && apt remove -y --purge build-essential cmake lsb-release wget libarrow-dev

COPY ./app /app/
WORKDIR /app
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED 1

# record some detail of the build, must be passed as --build-arg
ARG build_date
ARG commit_id
ARG commit_branch
ARG commit_message
ARG user_id=1001
ENV BUILD_DATE $build_date
ENV COMMIT_ID $commit_id
ENV COMMIT_BRANCH $commit_branch
ENV COMMIT_MESSAGE=$commit_message

EXPOSE 8080
WORKDIR /app
# Make the container run as non-root user
# https://developers.redhat.com/articles/2021/11/11/best-practices-building-images-pass-red-hat-container-certification#best_practice__3__set_group_ownership_and_file_permissions
RUN chown -R $user_id:0 /app && \
      chmod -R g=u /app
USER $user_id

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
