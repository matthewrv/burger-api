# Using multi-stage image build to create a production image without uv.

# First, build the application in the `/app` directory.
FROM ghcr.io/astral-sh/uv:python3.13-alpine AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Then create final image without uv
FROM python:3.13-alpine
COPY --from=builder --chown=app:app /app /app

# Add py-spy
ENV pip_install="pip3 install --disable-pip-version-check --no-cache-dir"
ADD https://github.com/benfred/py-spy/releases/download/v0.4.0/py_spy-0.4.0-py2.py3-none-manylinux_2_5_x86_64.manylinux1_x86_64.whl /tmp
RUN $pip_install auditwheel patchelf \
    && auditwheel repair /tmp/py_spy-0.4.0-py2.py3-none-manylinux_2_5_x86_64.manylinux1_x86_64.whl \
    && $pip_install /wheelhouse/*

# Add curl
RUN apk --no-cache add curl

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Run the FastAPI application by default
CMD ["uvicorn", "--loop", "uvloop", "--log-level", "error", "--no-use-colors", "--no-access-log", "--host", "0.0.0.0", "main:app"]
