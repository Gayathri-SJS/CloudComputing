#__copyright__   = "Copyright 2024, VISA Lab"
#__license__     = "MIT"

# Define global args
ARG FUNCTION_DIR="/home/app/"
ARG RUNTIME_VERSION="3.8"
ARG DISTRO_VERSION="3.12"

FROM alpine:latest
FROM python:${RUNTIME_VERSION}-slim AS python-alpine

#RUN apt-get update \
#    && apt-get install -y cmake ca-certificates libgl1-mesa-glx
RUN python${RUNTIME_VERSION} -m pip install --upgrade pip

FROM python-alpine AS build-image

# Include global args in this stage of the build
ARG FUNCTION_DIR
ARG RUNTIME_VERSION
# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

# Install Lambda Runtime Interface Client for Python
RUN python${RUNTIME_VERSION} -m pip install awslambdaric --target ${FUNCTION_DIR}


# Stage 3 - final runtime image
# Grab a fresh copy of the Python image
FROM python-alpine
# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}
# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}
# (Optional) Add Lambda Runtime Interface Emulator and use a script in the ENTRYPOINT for simpler local runs
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
RUN chmod 755 /usr/bin/aws-lambda-rie

# Install ffmpeg
RUN apt-get update 
RUN apt-get install -y ffmpeg
COPY torch-2.2.2-cp38-cp38-manylinux_2_17_aarch64.manylinux2014_aarch64.whl ${FUNCTION_DIR}
COPY torchvision-0.17.2-cp38-cp38-linux_aarch64.whl ${FUNCTION_DIR}

RUN python${RUNTIME_VERSION} -m pip install imutils --target ${FUNCTION_DIR}
RUN python${RUNTIME_VERSION} -m pip install requests --target ${FUNCTION_DIR}
RUN python${RUNTIME_VERSION} -m pip install opencv-python --target ${FUNCTION_DIR}
RUN python${RUNTIME_VERSION} -m pip install pillow --target ${FUNCTION_DIR}
RUN python${RUNTIME_VERSION} -m pip install facenet_pytorch --no-deps --target ${FUNCTION_DIR}
RUN python${RUNTIME_VERSION} -m pip install --no-cache-dir torch-2.2.2-cp38-cp38-manylinux_2_17_aarch64.manylinux2014_aarch64.whl --target ${FUNCTION_DIR}
RUN python${RUNTIME_VERSION} -m pip install --no-cache-dir torchvision-0.17.2-cp38-cp38-linux_aarch64.whl --target ${FUNCTION_DIR}

#RUN apk --no-cache add ffmpeg

# Copy handler function
COPY requirements.txt ${FUNCTION_DIR}
#COPY ffmpeg ${FUNCTION_DIR}
#COPY ffmpeg /usr/bin

RUN python${RUNTIME_VERSION} -m pip install -r requirements.txt --target ${FUNCTION_DIR}
COPY entry.sh /

# Copy function code
COPY handler.py ${FUNCTION_DIR}
RUN chmod 777 /entry.sh

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
ENTRYPOINT [ "/entry.sh" ]
CMD [ "handler.handler" ]
