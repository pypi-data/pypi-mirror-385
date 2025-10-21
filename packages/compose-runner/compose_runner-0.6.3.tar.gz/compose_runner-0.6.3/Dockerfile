FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .

# install build backend and hatch
RUN pip install --upgrade pip && pip install hatchling hatch-vcs hatch

# export dependencies using hatch and install with pip
RUN hatch dep show requirements > requirements.txt && pip install -r requirements.txt

COPY . .

# install the package with AWS extras so the ECS task has boto3, etc.
RUN pip install '.[aws]'

ENTRYPOINT ["compose-run"]
