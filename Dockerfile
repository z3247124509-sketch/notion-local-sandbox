ARG PYTHON_IMAGE=python:3.12.15-slim-bookworm@sha256:739ba32ae445e8d58f3d90feb85f83bebc8346f8dd280fa1eb5848f4ff1ed163
FROM ${PYTHON_IMAGE}
COPY requirements.lock /tmp/requirements.lock
COPY vendor/wheels/ /tmp/wheels/
RUN --network=none python -I -m pip install --no-index --find-links=/tmp/wheels --require-hashes --no-deps -r /tmp/requirements.lock && rm -rf /tmp/wheels /tmp/requirements.lock
COPY src/ /opt/kit/src/
COPY fixtures/ /workspace/
RUN mkdir /ipc && chown -R 10001:10001 /workspace /ipc && chmod 700 /workspace /ipc
USER 10001:10001
WORKDIR /tmp
ENTRYPOINT ["python", "-I", "-B", "/opt/kit/src/server.py"]
