ARG python_version=3.11
FROM mcr.microsoft.com/mirror/docker/library/python:${python_version}-slim

RUN apt update && apt install -y build-essential
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
      && pip install --no-cache-dir -r /app/requirements.txt

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=./

COPY ./app /app

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

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
