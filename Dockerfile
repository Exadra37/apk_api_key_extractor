ARG TAG=18.04

FROM ubuntu:${TAG}

ARG CONTAINER_USER="developer"
ARG LANGUAGE_CODE="en"
ARG COUNTRY_CODE="GB"
ARG ENCODING="UTF-8"

ARG LOCALE_STRING="${LANGUAGE_CODE}_${COUNTRY_CODE}"
ARG LOCALIZATION="${LOCALE_STRING}.${ENCODING}"

ARG OH_MY_ZSH_THEME="bira"

RUN apt update && apt -y upgrade && \
    apt -y install \
        locales \
        git \
        curl \
        inotify-tools \
        python3 \
        python3-pip \
        default-jdk \
        zsh && \

        echo "${LOCALIZATION} ${ENCODING}" > /etc/locale.gen && \
        locale-gen "${LOCALIZATION}" && \

        useradd -m -u 1000 -s /usr/bin/zsh "${CONTAINER_USER}" && \

        bash -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)" && \

        cp -v /root/.zshrc /home/"${CONTAINER_USER}"/.zshrc && \
        cp -rv /root/.oh-my-zsh /home/"${CONTAINER_USER}"/.oh-my-zsh && \
        sed -i "s/\/root/\/home\/${CONTAINER_USER}/g" /home/"${CONTAINER_USER}"/.zshrc && \
        sed -i s/ZSH_THEME=\"robbyrussell\"/ZSH_THEME=\"${OH_MY_ZSH_THEME}\"/g /home/${CONTAINER_USER}/.zshrc && \
        mkdir /home/"${CONTAINER_USER}"/workspace && \
        chown -R "${CONTAINER_USER}":"${CONTAINER_USER}" /home/"${CONTAINER_USER}"

ENV USER ${CONTAINER_USER}
ENV LANG "${LOCALIZATION}"
ENV LANGUAGE "${LOCALE_STRING}:${LANGUAGE_CODE}"
ENV PATH=/home/${CONTAINER_USER}/.local/bin:${PATH}
ENV LC_ALL "${LOCALIZATION}"

USER ${CONTAINER_USER}

RUN mkdir -p /home/${CONTAINER_USER}/.local/bin

# ENV HOME /
ENV PATH /usr/bin:$PATH

WORKDIR /home/${CONTAINER_USER}/workspace

ADD requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

RUN mkdir -p \
    /home/${CONTAINER_USER}/.local/share/apktool/framework \
    /home/${CONTAINER_USER}/apks_decoded \
    /home/${CONTAINER_USER}/apks_analyzed

CMD ["zsh"]
