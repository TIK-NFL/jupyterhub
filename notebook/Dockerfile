FROM quay.io/jupyter/base-notebook:hub-5.1.0


# ======================================================================================================================
# General packages and jupyterhub dependencies
#

USER 0
RUN apt-get update && \
    apt-get install -y vim curl wget jq patch pandoc git \
        texlive-xetex texlive-fonts-recommended texlive-plain-generic  \
        texlive-latex-extra texlive-fonts-recommended dvipng cm-super
USER 1000

# ======================================================================================================================
# Python modules
#

RUN pip install matplotlib numpy scipy scikit-learn pandas tensorflow networkx

# ======================================================================================================================
# Jupyter extensions
#

RUN pip install --upgrade ipywidgets nbconvert playwright ipython ipympl && \
    playwright install chromium

# ======================================================================================================================
# Jupyter kernels
#

# ---------------------------------------------------- BASH kernel -----------------------------------------------------
RUN pip install bash_kernel && \
    python -m bash_kernel.install

# --------------------------------------------------- Octave kernel ----------------------------------------------------
USER 0
RUN apt-get -y install octave

USER 1000
RUN pip install octave_kernel

COPY res/octave-logo-svg.svg /opt/conda/share/jupyter/kernels/octave/logo-svg.svg

# ----------------------------------------------------- C kernel -------------------------------------------------------
RUN pip install jupyter-c-kernel && \
    install_c_kernel --sys-prefix

COPY res/c-logo-svg.svg /opt/conda/share/jupyter/kernels/c/logo-svg.svg

# ----------------------------------------------------- R kernel -------------------------------------------------------
USER 0
RUN apt-get -y install r-base && \
    R -e 'install.packages("IRkernel")'
USER 1000
RUN R -e 'IRkernel::installspec()'

# ------------------------------------------------- Xeus-Clang kernel --------------------------------------------------
ENV PATH="${PATH}:/opt/mambaforge/bin"

USER 0
RUN MAMBAFORGE_RELEASE="23.3.1-1"; \
    INSTALL_SCRIPT_LOC="https://github.com/conda-forge/miniforge/releases/download"; \
    INSTALL_SCRIPT="Mambaforge-${MAMBAFORGE_RELEASE}-Linux-x86_64.sh"; \
    curl -OL "${INSTALL_SCRIPT_LOC}/${MAMBAFORGE_RELEASE}/${INSTALL_SCRIPT}" && \
    bash ${INSTALL_SCRIPT} -p /opt/mambaforge -b && \
    rm ${INSTALL_SCRIPT}

USER 1000
RUN mamba install -y xeus-cling -c conda-forge && \
    jupyter-kernelspec uninstall -y xcpp11 xcpp14  # only retain xcpp17


# ======================================================================================================================
# Patches
#


# ======================================================================================================================
# Customizations
#

RUN pip uninstall --yes nbclassic
# Disable Jupyter news and update announcements
RUN jupyter labextension disable "@jupyterlab/apputils-extension:announcements"
# Disable safeguard dialog for unsaved changes. Unsaved changes are handled by the Jupyterlab integration extension.
RUN jupyter labextension disable "@jupyterlab/application-extension:dirty"

# Custom startup script to support parameter passthrough via LTI (JWT) claims
USER 0

# Custom config
RUN sed -i 's/c.FileContentsManager.delete_to_trash = False/c.FileContentsManager.always_delete_dir = True/g' /etc/jupyter/jupyter_server_config.py

# Custom user server startup
COPY scripts/custom_user_server_startup /usr/local/bin/custom_user_server_startup
RUN chmod +x /usr/local/bin/custom_user_server_startup

RUN mkdir -p /data/metadata && chown root:root /data/metadata && chmod -R 700 /data/metadata && \
    mkdir -p /home/jovyan/__shared && chown jovyan:users /home/jovyan/__shared && \
    mkdir -p /home/jovyan/__submissions && chown jovyan:users /home/jovyan/__submissions && \
    mkdir -p /home/jovyan/work/__submission && chown jovyan:users /home/jovyan/work/__submission


# Switch to the standard jupyter user 'jovyan'
USER 1000
