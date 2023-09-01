# VisionSOM-RZ/x2L eMMC programming tool


## usage
```bash
./rzx2l-loader.py -p <serial port> -l <loader>  --image <boot image>

```
where:
<serial port> - path to serial port, i.e. /dev/ttyUSB0
<loader> - path to loader file in motorola S-record format
<boot image> - path to emmc boot partition image file in binary format

example usage:
```bash
./rzx2l-loader.py -p /dev/ttyUSB0 -l Flash_Writer_SCIF_VSOM_G2L_1GB_DDR4_1GB_1PCS.mot  --image boot.img
```
