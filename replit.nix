{ pkgs }: {
  deps = [
    pkgs.python3
    pkgs.python3Packages.pip
    pkgs.nodejs-18_x
    pkgs.nodePackages.npm
    pkgs.tesseract
    pkgs.opencv
    pkgs.pkg-config
    pkgs.cairo
    pkgs.pango
    pkgs.libpng
    pkgs.libjpeg
    pkgs.zlib
  ];
} 