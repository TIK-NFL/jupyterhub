FROM quay.io/jupyter/base-notebook:hub-5.0.0


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

# ---------------------------------------------------- Java kernel -----------------------------------------------------
USER 0
RUN apt-get install -y openjdk-18-jdk openjdk-18-jre-headless openjdk-18-source

USER 1000
RUN IJAVA_RELEASE="1.3.0" && \
    IJAVA_ARCHIVE_URL="https://github.com/SpencerPark/IJava/releases/download/v${IJAVA_RELEASE}/ijava-${IJAVA_RELEASE}.zip" && \
    IJAVA_TMP_DIR="/tmp/ijava" && \
    mkdir -p ${IJAVA_TMP_DIR} && \
    curl -L ${IJAVA_ARCHIVE_URL} -o ${IJAVA_TMP_DIR}/archive.zip && \
    unzip -d ${IJAVA_TMP_DIR} ${IJAVA_TMP_DIR}/archive.zip && \
    python ${IJAVA_TMP_DIR}/install.py --sys-prefix && \
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
# Disable Jupyter news and update announcements
RUN jupyter labextension disable "@jupyterlab/apputils-extension:announcements"
# Disable safeguard dialog for unsaved changes. Unsaved changes are handled by the Jupyterlab integration extension.
RUN jupyter labextension disable "@jupyterlab/application-extension:dirty"

# ----------------------------------------- Jupyterlab integration extension -------------------------------------------
USER 1000
RUN pip install --user git+https://github.com/TIK-NFL/jupyterlab-integration-extension@1.0.1


# Switch to the standard jupyter user 'jovyan'
USER 1000