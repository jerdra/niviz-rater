FROM python:3.8-slim-buster
ARG NODE_VERSION=16.13.0
ENV NVM_DIR=/root/.nvm
ENV PATH="/root/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"

RUN apt-get update \
  && apt install -y --no-install-recommends curl \
  && curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash \
  && . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION} \
  && . "$NVM_DIR/nvm.sh" && nvm use v${NODE_VERSION} \
  && . "$NVM_DIR/nvm.sh" && nvm alias default v${NODE_VERSION} \
  && echo "Using Node Version:" && node --version \
  && echo "Using NPM Version:" && npm --version


COPY . ./niviz-rater
RUN cd niviz-rater \
  && pip install -r requirements.txt \
  && pip install .

WORKDIR ./niviz-rater/niviz_rater/client
RUN npm run build
WORKDIR /

ENTRYPOINT ["niviz-rater"]
