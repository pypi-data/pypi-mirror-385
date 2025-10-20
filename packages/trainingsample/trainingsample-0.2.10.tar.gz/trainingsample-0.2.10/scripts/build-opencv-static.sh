#!/usr/bin/env bash
set -euo pipefail

# Build static OpenCV bundle for embedding in Python wheels
# This eliminates the need for users to install OpenCV system packages

OPENCV_VERSION="4.12.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BUILD_DIR="${PROJECT_ROOT}/opencv-build-tmp"
INSTALL_DIR="${PROJECT_ROOT}/third_party/opencv-static"
SIGNATURE_FILE="${INSTALL_DIR}/build_signature.txt"
BUILD_SIGNATURE="opencv-${OPENCV_VERSION}-static-codecs-jasper-no-itt-no-openjpeg"

echo "Building static OpenCV ${OPENCV_VERSION}..."
echo "Install directory: ${INSTALL_DIR}"

# Skip rebuild when signature matches desired configuration
if [ -d "${INSTALL_DIR}/lib" ] && [ -f "${INSTALL_DIR}/lib/libopencv_world.a" ] && [ -f "${SIGNATURE_FILE}" ]; then
    if grep -qx "${BUILD_SIGNATURE}" "${SIGNATURE_FILE}"; then
        echo "Static OpenCV already built at ${INSTALL_DIR} (signature match)"
        exit 0
    fi

    echo "Existing static OpenCV bundle does not match desired configuration. Rebuilding..."
    rm -rf "${INSTALL_DIR}"
fi

# Create build directory
mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

# Download OpenCV source if not already present
if [ ! -d "opencv-${OPENCV_VERSION}" ]; then
    echo "Downloading OpenCV ${OPENCV_VERSION}..."
    curl -L "https://github.com/opencv/opencv/archive/refs/tags/${OPENCV_VERSION}.tar.gz" \
        -o "opencv-${OPENCV_VERSION}.tar.gz"
    tar -xzf "opencv-${OPENCV_VERSION}.tar.gz"
fi

# Configure CMake build
echo "Configuring CMake build..."
cmake -S "opencv-${OPENCV_VERSION}" \
      -B build \
      -DCMAKE_BUILD_TYPE=Release \
      -DBUILD_LIST=core,imgproc,imgcodecs,highgui,video,videoio,calib3d,features2d,photo \
      -DBUILD_SHARED_LIBS=OFF \
      -DBUILD_opencv_world=ON \
      -DOPENCV_FORCE_3RDPARTY_BUILD=ON \
      -DBUILD_JPEG=ON \
      -DBUILD_PNG=ON \
      -DBUILD_TIFF=ON \
      -DBUILD_WEBP=ON \
      -DBUILD_ZLIB=ON \
      -DBUILD_JASPER=ON \
      -DWITH_JPEG=ON \
      -DWITH_PNG=ON \
      -DWITH_TIFF=ON \
      -DWITH_WEBP=ON \
      -DWITH_ZLIB=ON \
      -DWITH_JASPER=ON \
      -DBUILD_TESTS=OFF \
      -DBUILD_PERF_TESTS=OFF \
      -DBUILD_EXAMPLES=OFF \
      -DBUILD_opencv_apps=OFF \
      -DBUILD_DOCS=OFF \
      -DWITH_IPP=OFF \
      -DWITH_OPENCL=OFF \
      -DWITH_CUDA=OFF \
      -DWITH_OPENJPEG=OFF \
      -DWITH_FFMPEG=OFF \
      -DWITH_GSTREAMER=OFF \
      -DWITH_V4L=OFF \
      -DWITH_GTK=OFF \
      -DWITH_QT=OFF \
      -DWITH_OPENEXR=OFF \
      -DWITH_ITT=OFF \
      -DCMAKE_INSTALL_PREFIX="${INSTALL_DIR}"

# Build opencv_world (single unified library)
echo "Building OpenCV (this may take several minutes)..."
cmake --build build --config Release --target opencv_world -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 2)

# Install to third_party/opencv-static
echo "Installing to ${INSTALL_DIR}..."
cmake --install build --config Release

# Copy bundled third-party codec archives into the install lib directory and
# provide canonical aliases (libjpeg.a, libwebp.a, …) for the linker.
CODEC_LIB_DIR="${BUILD_DIR}/build/3rdparty/lib"
mkdir -p "${INSTALL_DIR}/lib"

declare -a CODEC_MAPPINGS=(
    "liblibjpeg-turbo.a:libjpeg.a"
    "liblibpng.a:libpng.a"
    "liblibtiff.a:libtiff.a"
    "liblibwebp.a:libwebp.a"
    "libzlib.a:libz.a"
    "liblibjasper.a:libjasper.a"
)

for mapping in "${CODEC_MAPPINGS[@]}"; do
    SRC_ARCHIVE="${CODEC_LIB_DIR}/${mapping%%:*}"
    CANONICAL_NAME="${mapping%%:*}"
    LINK_NAME="${mapping##*:}"

    if [ ! -f "${SRC_ARCHIVE}" ]; then
        echo "ERROR: Expected third-party archive ${SRC_ARCHIVE} was not produced by the OpenCV build"
        find "${CODEC_LIB_DIR}" -maxdepth 1 -type f -name 'lib*.a' | sed "s#^#  #"
        exit 1
    fi

    cp -f "${SRC_ARCHIVE}" "${INSTALL_DIR}/lib/${CANONICAL_NAME}"
    ln -sf "${CANONICAL_NAME}" "${INSTALL_DIR}/lib/${LINK_NAME}"
done

# Verify installation - check both lib and lib64 (manylinux uses lib64)
if [ -d "${INSTALL_DIR}/lib64" ]; then
    # Move from lib64 to lib for consistency (copy to handle reruns safely)
    mkdir -p "${INSTALL_DIR}/lib"
    cp -a "${INSTALL_DIR}/lib64/." "${INSTALL_DIR}/lib/"
    rm -rf "${INSTALL_DIR}/lib64"
fi

if [ ! -f "${INSTALL_DIR}/lib/libopencv_world.a" ]; then
    echo "ERROR: libopencv_world.a not found after installation"
    echo "Contents of ${INSTALL_DIR}:"
    ls -R "${INSTALL_DIR}"
    exit 1
fi

# Ensure third-party codecs were produced as static archives
REQUIRED_ARCHIVES=(
    "libjpeg.a"
    "libpng.a"
    "libtiff.a"
    "libwebp.a"
    "libz.a"
    "libjasper.a"
)

for archive in "${REQUIRED_ARCHIVES[@]}"; do
    if [ ! -f "${INSTALL_DIR}/lib/${archive}" ]; then
        echo "ERROR: Required static archive ${archive} not found in ${INSTALL_DIR}/lib"
        echo "Available archives:"
        find "${INSTALL_DIR}" -maxdepth 2 -type f -name 'lib*.a' | sed "s#^#  #"
        exit 1
    fi
done

printf '%s\n' "${BUILD_SIGNATURE}" > "${SIGNATURE_FILE}"

echo "Static OpenCV built successfully!"
echo "Library: ${INSTALL_DIR}/lib/libopencv_world.a"
echo "Headers: ${INSTALL_DIR}/include/opencv4/"

# Clean up build directory to save space
cd "${PROJECT_ROOT}"
rm -rf "${BUILD_DIR}"

echo "Build complete!"
