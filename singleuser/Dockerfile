FROM quay.io/jupyterhub/singleuser:main


# ======================================================================================================================
# General packages and jupyterhub dependencies
#

USER 0
RUN apt update; \
    apt install -y vim curl wget jq

USER 1000
RUN pip install --upgrade ipywidgets matplotlib numpy scipy scikit-learn


# ======================================================================================================================
# Jupyter kernels
#

USER 1000

# ---------------------------------------------------- BASH kernel -----------------------------------------------------
RUN pip install bash_kernel; \
    python -m bash_kernel.install

# --------------------------------------------------- Octave kernel ----------------------------------------------------
RUN apt-get -y install octave; \
    pip install octave_kernel

# ----------------------------------------------------- C kernel -------------------------------------------------------
RUN pip install jupyter-c-kernel; \
    install_c_kernel --sys-prefix

# ----------------------------------------------------- R kernel -------------------------------------------------------
USER 0
RUN apt-get -y install r-base; \
    R -e 'install.packages("IRkernel")'
USER 1000
RUN R -e 'IRkernel::installspec()'

# ------------------------------------------------- Xeus-Clang kernel --------------------------------------------------
USER 0
ENV PATH="${PATH}:/opt/mambaforge/bin"

RUN MAMBAFORGE_RELEASE="23.3.1-1"; \
    INSTALL_SCRIPT_LOC="https://github.com/conda-forge/miniforge/releases/download"; \
    INSTALL_SCRIPT="Mambaforge-${MAMBAFORGE_RELEASE}-Linux-x86_64.sh"; \
    curl -OL "${INSTALL_SCRIPT_LOC}/${MAMBAFORGE_RELEASE}/${INSTALL_SCRIPT}"; \
    bash ${INSTALL_SCRIPT} -p /opt/mambaforge -b; \
    rm ${INSTALL_SCRIPT}

RUN mamba create -n cling; \
    mamba install -y xeus-cling -c conda-forge

# ----------------------------------------------------------------------------------------------------------------------


# Switch to the standard jupyter user 'jovyan'
USER 1000