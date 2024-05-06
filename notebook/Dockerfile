FROM quay.io/jupyter/base-notebook:hub-4.0.2


# ======================================================================================================================
# General packages and jupyterhub dependencies
#

# Use the jupyterhub current revision 135be724 succseeding a bugfix 3b2af296 which is essential for the integration.
# As there are no published releases/tags since then, the current revision from the main branch is used.
# TODO: Use a newer release tag (^4.0.2) as soon as it is available.
ARG JUPYTERHUB_VERSION=135be724

RUN pip install --no-cache --upgrade --upgrade-strategy only-if-needed \
    https://github.com/jupyterhub/jupyterhub/archive/${JUPYTERHUB_VERSION}.tar.gz

USER 0
RUN apt-get update; \
    apt-get install -y vim curl wget jq patch pandoc texlive-xetex texlive-fonts-recommended texlive-plain-generic
USER 1000

# ======================================================================================================================
# Jupyter extensions
#

RUN pip install --upgrade ipywidgets matplotlib numpy scipy scikit-learn nbconvert playwright; \
    playwright install chromium

# ======================================================================================================================
# Jupyter kernels
#

# ---------------------------------------------------- BASH kernel -----------------------------------------------------
RUN pip install bash_kernel; \
    python -m bash_kernel.install

# --------------------------------------------------- Octave kernel ----------------------------------------------------
USER 0
RUN apt-get -y install octave

USER 1000
RUN pip install octave_kernel

COPY res/octave-logo-svg.svg /opt/conda/share/jupyter/kernels/octave/logo-svg.svg

# ----------------------------------------------------- C kernel -------------------------------------------------------
RUN pip install jupyter-c-kernel; \
    install_c_kernel --sys-prefix

COPY res/c-logo-svg.svg /opt/conda/share/jupyter/kernels/c/logo-svg.svg

# ----------------------------------------------------- R kernel -------------------------------------------------------
USER 0
RUN apt-get -y install r-base; \
    R -e 'install.packages("IRkernel")'
USER 1000
RUN R -e 'IRkernel::installspec()'

# ------------------------------------------------- Xeus-Clang kernel --------------------------------------------------
ENV PATH="${PATH}:/opt/mambaforge/bin"

RUN MAMBAFORGE_RELEASE="23.3.1-1"; \
    INSTALL_SCRIPT_LOC="https://github.com/conda-forge/miniforge/releases/download"; \
    INSTALL_SCRIPT="Mambaforge-${MAMBAFORGE_RELEASE}-Linux-x86_64.sh"; \
    curl -OL "${INSTALL_SCRIPT_LOC}/${MAMBAFORGE_RELEASE}/${INSTALL_SCRIPT}"; \
    bash ${INSTALL_SCRIPT} -p /opt/mambaforge -b; \
    rm ${INSTALL_SCRIPT}

RUN mamba install -y xeus-cling -c conda-forge; \
    jupyter-kernelspec uninstall -y xcpp11 xcpp14  # only retain xcpp17

# ---------------------------------------------------- Java kernel -----------------------------------------------------
USER 0
RUN apt-get install -y openjdk-18-jdk openjdk-18-jre-headless openjdk-18-source

USER 1000
RUN IJAVA_RELEASE="1.3.0"; \
    IJAVA_ARCHIVE_URL="https://github.com/SpencerPark/IJava/releases/download/v${IJAVA_RELEASE}/ijava-${IJAVA_RELEASE}.zip"; \
    IJAVA_TMP_DIR="/tmp/ijava"; \
    mkdir -p ${IJAVA_TMP_DIR}; \
    curl -L ${IJAVA_ARCHIVE_URL} -o ${IJAVA_TMP_DIR}/archive.zip; \
    unzip -d ${IJAVA_TMP_DIR} ${IJAVA_TMP_DIR}/archive.zip; \
    python ${IJAVA_TMP_DIR}/install.py --sys-prefix; \
    rm -rf ${IJAVA_TMP_DIR}

COPY res/java-logo-svg.svg /opt/conda/share/jupyter/kernels/java/logo-svg.svg


# ======================================================================================================================
# Patches
#

USER 0
COPY patches/*.py.patch /tmp/
RUN patch /opt/conda/lib/python3.11/http/cookies.py < /tmp/cookies.py.patch && \
    patch /opt/conda/lib/python3.11/site-packages/jupyter_server/serverapp.py < /tmp/serverapp.py.patch
USER 1000

# ======================================================================================================================
# Customizations
#

RUN pip uninstall --yes nbclassic
RUN jupyter labextension disable "@jupyterlab/apputils-extension:announcements"

# --------------------------------------------------- jpyintegext ------------------------------------------------------
#USER 1000
#COPY --chown=1000:100 res/jpyintegext-1.0.0.tar.gz .local/share/packages/jpyintegext.tar.gz
#RUN pip install --user .local/share/packages/jpyintegext.tar.gz


# Switch to the standard jupyter user 'jovyan'
USER 1000