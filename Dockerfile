# PrepSheet 

ARG BASE_PLATFORM=linux/amd64
FROM --platform=${BASE_PLATFORM} public.ecr.aws/e1h7x4a2/plow-cloud-agents:base-ef0019372ff8bca593611b31ebd2e08f9f1458ff@sha256:a8a2f97ad78b8192d80a984dce81d3bf5a9a883d18cb7b677704913a09b56aee


COPY runtime/SOUL.md /var/lib/hermes/SOUL.md
COPY LICENSE NOTICE /usr/share/doc/prepsheet/

RUN apt-get update -qq \
 && apt-get install -y --no-install-recommends \
      libpango-1.0-0 \
      libpangoft2-1.0-0 \
      libharfbuzz0b \
      libfontconfig1 \
      libcairo2 \
      libgdk-pixbuf-2.0-0 \
      fonts-liberation \
 && /opt/hermes/.venv/bin/python3 -m ensurepip --upgrade \
 && /opt/hermes/.venv/bin/python3 -m pip install --no-cache-dir weasyprint \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY ps-setup/            /opt/hermes/skills/ps-setup/
COPY ps-dawn/             /opt/hermes/skills/ps-dawn/
COPY ps-dossier/          /opt/hermes/skills/ps-dossier/
COPY ps-query/            /opt/hermes/skills/ps-query/
COPY ps-schedule/         /opt/hermes/skills/ps-schedule/
COPY ps-osint/            /opt/hermes/skills/ps-osint/
COPY ps-shared/           /opt/hermes/skills/ps-shared/


RUN find /opt/hermes/skills -mindepth 1 -type d -exec chmod 0755 {} + \
 && find /opt/hermes/skills -mindepth 1 -type f ! -perm -u+x -exec chmod 0644 {} + \
 && find /opt/hermes/skills -mindepth 1 -type f -perm -u+x -exec chmod 0755 {} + \
 && chmod 0644 /var/lib/hermes/SOUL.md


COPY ps-shared/ /opt/plow/ps-shared/
RUN chown -R root:root /opt/plow \
 && find /opt/plow -type d -exec chmod 0755 {} + \
 && find /opt/plow -type f -exec chmod 0644 {} + \
 && find /opt/plow -type f -name '*.py' -exec chmod 0755 {} +


# Usage reporting is the base's own Agent Index reporter (pinned client + s6
# "agent-index" service). It reads AGENT_ID; the Plow cloud passes no
# environment, so the id is baked here. Compose sets the same value.
ENV AGENT_ID=PrepSheet
