#-------------------------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See https://go.microsoft.com/fwlink/?linkid=2090316 for license information.
#-------------------------------------------------------------------------------------------------------------

FROM python:3-slim

# Enable if using Proxy, and building manually
#ENV DEBIAN_FRONTEND=noninteractive
#ENV http_proxy="http://127.0.0.1:9080" HTTP_PROXY="http://127.0.0.1:9080" https_proxy="http://127.0.0.1:9080" HTTPS_PROXY="http://127.0.0.1:9080"

# Or your actual UID, GID on Linux if not the default 1000
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
# Avoid warnings by switching to noninteractive
# But don't use ENV, coz ENV persists in the Containers too
ARG DEBIAN_FRONTEND=noninteractive

# Configure apt and install packages
RUN apt-get update \
    && apt-get -y install --no-install-recommends --no-install-suggests build-essential git zsh 2>&1 \
    && sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh) --unattended" \
    && sed -i 's/plugins=(git)/plugins=(gitfast\ alias-finder\ battery\ colorize\ common-aliases\ cp\ extract\ fancy-ctrl-z\ jsontools\ python\ pyenv\ urltools)/g' ~/.zshrc \
    # Verify git, process tools, lsb-release (useful for CLI installs) installed
    # && apt-get -y install --no-install-recommends --no-install-suggests apt-utils procps lsb-release git zsh 2>&1 \
    # #
    # # Create a non-root user to use if preferred - see https://aka.ms/vscode-remote/containers/non-root-user.
    # && groupadd --gid $USER_GID $USERNAME \
    # && useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME \
    # # [Optional] Add sudo support for non-root user
    # && apt-get install -y sudo \
    # && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    # && chmod 0440 /etc/sudoers.d/$USERNAME \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

#ENTRYPOINT [ "/bin/zsh" ]
# Switch back to dialog for any ad-hoc use of apt-get
#ENV DEBIAN_FRONTEND=
