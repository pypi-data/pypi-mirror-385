DOCKERFILE_CONTENT = """# ---------- Build Stage ----------
FROM alpine:3.22 AS build

# Set uv config
ENV XDG_BIN_HOME="/usr/local/bin"
ENV UV_COMPILE_BYTECODE="1"
ENV UV_LINK_MODE="copy"
ENV UV_NO_CACHE="1"
ENV UV_PROJECT_ENVIRONMENT="/opt/uv/venv"

# Set the default app dir
ENV APP_DIR="/app"

# Set the location of the virtual environment
ENV PATH="${UV_PROJECT_ENVIRONMENT}/bin:$PATH"

# Set default shell to ash and enable pipefail
SHELL ["/bin/ash", "-o", "pipefail", "-c"]

# System packages to build CKAN requirements and plugins
RUN apk add --no-cache \\
    git>=2.49 \\
    curl>=8.14 \\
    ca-certificates \\
    clang>=20.1 \\
    gcc>=14.2 \\
    linux-headers>=6.14 \\
    musl-dev>=1.2 \\
    libmagic>=5.46 \\
    postgresql17-client>=17.6 \\
    postgresql17-dev>=17.6 && \\
    ln -s /usr/bin/clang /usr/bin/musl-clang

# Install uv
RUN curl --retry 5 --retry-delay 3 --proto '=https' --tlsv1.2 -Ls https://github.com/astral-sh/uv/releases/download/0.7.22/uv-installer.sh | sh

WORKDIR ${APP_DIR}

# Copy the pyproject.toml
COPY pyproject.toml ${APP_DIR}/pyproject.toml

# Initalize venv
RUN uv venv

# Copy CKAN required files and directories
COPY src/ckan /app/src/ckan
COPY extensions /app/extensions

# Install uwsgi
RUN uv add uwsgi

# Sync CKAN pilot project
RUN uv sync --all-groups

# ---------- Final Stage ----------
FROM alpine:3.22 AS final

# Set uv config
ENV XDG_BIN_HOME="/usr/local/bin"
ENV UV_COMPILE_BYTECODE="1"
ENV UV_LINK_MODE="copy"
ENV UV_NO_CACHE="1"
ENV UV_PROJECT_ENVIRONMENT="/opt/uv/venv"

# Set the default app dir
ENV APP_DIR="/app"
WORKDIR ${APP_DIR}

# Set the location of the virtual environment
ENV PATH="${UV_PROJECT_ENVIRONMENT}/bin:$PATH"

# Set default shell to ash and enable pipefail
SHELL ["/bin/ash", "-o", "pipefail", "-c"]

# Copy venv from build stage and other requirements
COPY --from=build /opt/uv/venv /opt/uv/venv
COPY --from=build ${APP_DIR}/uv.lock ${APP_DIR}/uv.lock
COPY --from=build ${APP_DIR}/pyproject.toml ${APP_DIR}/pyproject.toml
COPY --from=build ${APP_DIR}/extensions ${APP_DIR}/extensions
COPY --from=build ${APP_DIR}/src/ckan ${APP_DIR}/src/ckan
# Copy .python-version so we can install correct version in new stage
COPY .python-version ${APP_DIR}/.python-version
# Copy uv binaries
COPY --from=build /usr/local/bin/uv /usr/local/bin/uv

# Install necessary packages to run CKAN
RUN apk add --no-cache \\
        git>=2.49 \\
        curl>=8.14 \\
        ca-certificates \\
        # # Required for CKAN
        libmagic>=5.46 \\
        postgresql17-client>=17.6

# Set python version var and install python
RUN uv python install $(cat /app/.python-version)

# Sync CKAN pilot project
RUN uv sync --all-groups

# Copy CKAN generated ini
{ckan_ini}

# Install additional system packages
{additional_system_packages}

# Copy prerun script as entrypoint and set entrypoint
COPY compose-dev/services/ckan/image/ /app/src/ckan
ENTRYPOINT [ "sh", "/app/src/ckan/docker-entrypoint.sh" ]

CMD {cmd}"""
