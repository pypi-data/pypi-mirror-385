from enum import Enum,IntEnum

class Chip(Enum):
    tpu_6_0 = 1
    tpul_6_0 = 2
    tpub_7_1 = 3
    tpul_8_0 = 4
    tpub_9_0 = 5
    tpul_8_1 = 6
    tpu_6_0_e = 7
    tpub_9_0_rv = 8

Chip.tpu_6_0.str = "tpu_6_0"
Chip.tpul_6_0.str = "tpul_6_0"
Chip.tpub_7_1.str = "tpub_7_1"
Chip.tpub_9_0.str = "tpub_9_0"
Chip.tpub_9_0_rv.str = "tpub_9_0_rv"
Chip.tpul_8_0.str = "tpul_8_0"
Chip.tpul_8_1.str = "tpul_8_1"
Chip.tpu_6_0_e.str = "tpu_6_0_e"

class ErrorCode(IntEnum):
    PplLocalAddrAssignErr = 0x11,
    FileErr = 0x12,
    LlvmFeErr = 0x13,
    PplFeErr = 0x14,
    PplOpt1Err = 0x15,
    PplOpt2Err = 0x16,
    PplFinalErr = 0x17,
    PplTransErr = 0x18,
    EnvErr = 0x19,
    PplL2AddrAssignErr = 0x1A,
    PplShapeInferErr = 0x1B,
    PplSetMemRefShapeErr = 0x1C,
    ToPplErr = 0x1D,
    PplTensorConvErr = 0x1E,
    PplDynBlockErr = 0x1F,
