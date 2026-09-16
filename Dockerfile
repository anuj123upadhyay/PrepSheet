# PrepSheet 

ARG BASE_PLATFORM=linux/amd64
FROM --platform=${BASE_PLATFORM} public.ecr.aws/e1h7x4a2/plow-cloud-agents:base-cd2a898d673812621bae6764560e455807e9818e@sha256:bfd4980f361a551e62569f8c2eb717c1076d0b8be3a0499b869eaece151336a4


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


COPY vendor/client.pin /opt/plow/agent-index-client.pin
RUN set -eu; \
    sha="$(sed -n 's/^sha=//p' /opt/plow/agent-index-client.pin)"; \
    want="$(sed -n 's/^sha256=//p' /opt/plow/agent-index-client.pin)"; \
    path="$(sed -n 's/^path=//p' /opt/plow/agent-index-client.pin)"; \
    curl -fsS --max-time 60 -o /opt/plow/agent-index-client.py \
      "https://raw.githubusercontent.com/plow-pbc/agent-index-client/${sha}/${path}"; \
    got="$(sha256sum /opt/plow/agent-index-client.py | cut -d' ' -f1)"; \
    [ "$got" = "$want" ] || { echo "agent-index client e $got, o pin diz $want" >&2; exit 1; }; \
    chmod 0644 /opt/plow/agent-index-client.py

COPY image/s6-overlay/ /etc/s6-overlay/
RUN chmod 0755 /etc/s6-overlay/s6-rc.d/agent-index/run